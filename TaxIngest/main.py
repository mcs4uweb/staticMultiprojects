from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tax Document RAG Assistant")

# Load vector store on startup
try:
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding
    )
    logger.info("✅ Vector store loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load vector store: {e}")
    vectorstore = None

class TaxQuery(BaseModel):
    question: str
    k: int = 3
    form_type: Optional[str] = None  # Filter by form type (W-2, Schedule A, etc.)

class TaxResult(BaseModel):
    content: str
    source: str
    form_type: str

@app.post("/tax-query", response_model=List[TaxResult])
def tax_query(query: TaxQuery):
    if not vectorstore:
        raise HTTPException(status_code=500, detail="Vector store not available")
    
    # Build search args
    search_kwargs = {"k": query.k}
    
    # Filter by tax form type if specified
    if query.form_type:
        search_kwargs["filter"] = {"file_type": query.form_type}
    
    try:
        results = vectorstore.similarity_search(query.question, **search_kwargs)
        return [
            TaxResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                form_type=doc.metadata.get("file_type", "unknown")
            )
            for doc in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    doc_count = vectorstore._collection.count() if vectorstore else 0
    return {
        "status": "ready" if vectorstore else "error",
        "documents_loaded": doc_count
    }

@app.delete("/reset")
def reset_db():
    """Reset the vector database (for development)"""
    import shutil
    shutil.rmtree("./chroma_db", ignore_errors=True)
    return {"message": "Database reset complete"}