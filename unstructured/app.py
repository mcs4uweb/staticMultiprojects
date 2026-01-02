from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from ingest import UniversalIngestor

app = FastAPI(title="Document LLM Ingestor API")

# Load vector DB on startup
ingestor = UniversalIngestor()

class QueryRequest(BaseModel):
    question: str
    k: int = 3

class SearchResult(BaseModel):
    content: str
    source: str

@app.post("/query", response_model=List[SearchResult])
def query_documents(request: QueryRequest):
    try:
        results = ingestor.query(request.question, k=request.k)
        return [
            SearchResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown")
            )
            for doc in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ready"}