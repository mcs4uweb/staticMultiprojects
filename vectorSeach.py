# AIDEV-NOTE: This script demonstrates how to perform vector search using AWS Bedrock and Amazon OpenSearch Serverless.
# It requires the following libraries:
# pip install boto3 opensearch-py

import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4Signer

# =============================================================================
# Configuration
# =============================================================================
# AIDEV-NOTE: Replace these with your actual AWS and OpenSearch details.
AWS_REGION = 'us-east-1'
BEDROCK_EMBEDDING_MODEL_ID = 'amazon.titan-embed-text-v1'

# AIDEV-NOTE: Replace with your OpenSearch Serverless endpoint and index name.
# The endpoint typically looks like: https://your-endpoint.us-east-1.aoss.amazonaws.com
OPENSEARCH_HOST = 'your-endpoint.us-east-1.aoss.amazonaws.com'
OPENSEARCH_INDEX_NAME = 'my-documents'

# =============================================================================
# AWS Clients and Signers
# =============================================================================
try:
    # AIDEV-NOTE: Initialize the Bedrock Runtime client to get embeddings.
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION
    )

    # AIDEV-NOTE: Create a signer for OpenSearch authentication.
    credentials = boto3.Session().get_credentials()
    aws_auth = AWSV4Signer(credentials, AWS_REGION, 'aoss')

    # AIDEV-NOTE: Initialize the OpenSearch client with AWS authentication.
    opensearch_client = OpenSearch(
        hosts=[{'host': OPENSEARCH_HOST, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
except Exception as e:
    print(f"Error initializing AWS clients: {e}")
    exit()

def get_text_embedding(text):
    """
    Generates a text embedding using an AWS Bedrock model.
    """
    try:
        # AIDEV-NOTE: The payload structure is specific to the model.
        body = json.dumps({"inputText": text})
        
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get("embedding")
        return embedding
        
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def create_opensearch_index():
    """
    Creates an OpenSearch index with a vector field mapping.
    The dimension must match the embedding model output. Titan v1 is 1536.
    """
    try:
        index_body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "vector_field": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "faiss"
                        }
                    }
                }
            }
        }
        
        if not opensearch_client.indices.exists(index=OPENSEARCH_INDEX_NAME):
            response = opensearch_client.indices.create(
                index=OPENSEARCH_INDEX_NAME,
                body=index_body
            )
            print(f"Index creation response: {response}")
        else:
            print(f"Index '{OPENSEARCH_INDEX_NAME}' already exists.")
            
    except Exception as e:
        print(f"Error creating OpenSearch index: {e}")

def ingest_data_to_opensearch(documents):
    """
    Generates embeddings for a list of documents and ingests them into OpenSearch.
    """
    print("Ingesting documents...")
    for i, doc in enumerate(documents):
        embedding = get_text_embedding(doc["text"])
        if embedding:
            document_body = {
                "text": doc["text"],
                "vector_field": embedding
            }
            # AIDEV-NOTE: Index the document in OpenSearch.
            response = opensearch_client.index(
                index=OPENSEARCH_INDEX_NAME,
                body=document_body,
                id=i,  # Simple ID for this example
                refresh=True
            )
            print(f"Indexed document {i}: {response['result']}")

def search_documents(query_text):
    """
    Performs a vector search for the given query text.
    """
    print(f"\nSearching for documents similar to: '{query_text}'")
    query_embedding = get_text_embedding(query_text)
    
    if query_embedding:
        # AIDEV-NOTE: Define the k-NN search query.
        search_query = {
            "size": 5, # Number of results to return
            "query": {
                "knn": {
                    "vector_field": {
                        "vector": query_embedding,
                        "k": 5
                    }
                }
            },
            "_source": ["text"] # Only return the text field
        }
        
        response = opensearch_client.search(
            body=search_query,
            index=OPENSEARCH_INDEX_NAME
        )
        
        print("\n--- Search Results ---")
        if response['hits']['hits']:
            for hit in response['hits']['hits']:
                source = hit['_source']
                score = hit['_score']
                print(f"Score: {score:.4f}, Text: {source['text']}")
        else:
            print("No matching documents found.")

# =============================================================================
# Main Execution
# =============================================================================
if __name__ == "__main__":
    # AIDEV-NOTE: Sample documents to ingest.
    sample_documents = [
        {"text": "The quick brown fox jumps over the lazy dog."},
        {"text": "A golden retriever is a very friendly pet."},
        {"text": "What do you call a fake noodle? An impasta."},
        {"text": "The sun is shining and the birds are chirping."},
        {"text": "Cats are known for their playful and independent nature."},
        {"text": "Hummingbirds are tiny birds that can hover in mid-air."},
    ]
    
    # AIDEV-NOTE: First, create the index if it doesn't exist.
    create_opensearch_index()
    
    # AIDEV-NOTE: Ingest the sample documents.
    ingest_data_to_opensearch(sample_documents)
    
    # AIDEV-NOTE: Perform a search with a new query.
    search_query = "What's a joke about pasta?"
    search_documents(search_query)