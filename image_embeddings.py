import os
import json
import boto3
import numpy as np
import faiss
from io import BytesIO
from typing import List, Dict
from PIL import Image
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings

# ----------------------------
# Configuration
# ----------------------------
AWS_REGION = "us-gov-west-1"
S3_BUCKET = "your-unique-doc-bucket"  # ← CHANGE THIS
TEXTRACT_ROLE_ARN = None  # Not needed for basic sync calls

# Bedrock & S3 clients
bedrock = boto3.client(service_name="bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)
textract = boto3.client("textract", region_name=AWS_REGION)

# Embedding model (choose one)
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
# Or: "cohere.embed-english-v3"

# Initialize LangChain Bedrock embeddings
embeddings = BedrockEmbeddings(
    model_id=EMBEDDING_MODEL_ID,
    client=bedrock,
    region_name=AWS_REGION,
    normalize=True  # ✅ Normalization built-in for Titan v2
)

# ----------------------------
# Step 1: Extract text from an image using Amazon Textract
# ----------------------------
def extract_text_from_image_s3(bucket: str, key: str) -> str:
    """Use Textract to extract text from image in S3"""
    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": bucket, "Name": key}}
    )
    text = " ".join([block["Text"] for block in response["Blocks"] if block["BlockType"] == "LINE"])
    return text

# Example: Assume you have image files in S3
image_keys = ["documents/form1.jpg", "documents/xray_notes.png"]
text_documents = []

# Add existing text sources
text_documents.append(
    Document(page_content="Patient discharged after successful surgery.", metadata={"source": "discharge_summary.txt", "type": "text"})
)

# Process images via Textract
for img_key in image_keys:
    try:
        extracted_text = extract_text_from_image_s3(S3_BUCKET, img_key)
        if extracted_text.strip():
            text_documents.append(
                Document(
                    page_content=extracted_text,
                    metadata={"source": img_key, "type": "textract_image"}
                )
            )
    except Exception as e:
        print(f"⚠️ Textract failed for {img_key}: {e}")

print(f"✅ Loaded {len(text_documents)} documents (text + Textract images)")

# ----------------------------
# Step 2: Split all documents
# ----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks: List[Document] = text_splitter.split_documents(text_documents)
print(f"✅ Split into {len(chunks)} chunks")

# ----------------------------
# Step 3: Generate embeddings using Amazon Bedrock
# ----------------------------
texts = [chunk.page_content for chunk in chunks]

# LangChain handles batching and normalization (for Titan v2)
# For Cohere, normalization is automatic; for Titan, set normalize=True above
embedding_vectors = embeddings.embed_documents(texts)  # Returns list of lists

# Convert to numpy float32
embeddings_np = np.array(embedding_vectors).astype("float32")

# ----------------------------
# Step 4: Build FAISS index (cosine similarity)
# ----------------------------
dimension = embeddings_np.shape[1]

# Titan v2 with normalize=True → use IndexFlatIP (inner product = cosine)
index = faiss.IndexFlatIP(dimension)
index.add(embeddings_np)

print(f"✅ FAISS index built with {index.ntotal} vectors")

# ----------------------------
# Step 5: Save to S3
# ----------------------------
# FAISS index
faiss_buffer = BytesIO()
faiss.write_index(index, faiss_buffer)
faiss_buffer.seek(0)
s3_client.upload_fileobj(faiss_buffer, S3_BUCKET, "faiss/index.faiss")

# Metadata
metadata = [
    {
        "content": chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content,
        "source": chunk.metadata["source"],
        "type": chunk.metadata["type"]
    }
    for chunk in chunks
]
s3_client.put_object(
    Bucket=S3_BUCKET,
    Key="faiss/index_metadata.json",
    Body=json.dumps(metadata, indent=2),
    ContentType="application/json"
)

print(f"✅ Index and metadata saved to s3://{S3_BUCKET}/faiss/")