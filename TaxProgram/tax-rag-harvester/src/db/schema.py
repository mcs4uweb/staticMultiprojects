"""
ChromaDB Schema and Utilities

Defines the vector database schema and collection management for tax documents.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
import yaml

logger = logging.getLogger(__name__)


@dataclass
class TaxCollectionSchema:
    """Schema for tax document collections."""
    name: str
    description: str
    
    # Metadata fields for filtering
    metadata_fields = {
        "source_doc": "string",      # Original filename
        "doc_type": "string",        # form, instructions, publication
        "form_number": "string",     # 1040, 8889, etc.
        "tax_year": "int",           # 2024
        "section": "string",         # Part I, Schedule A
        "line_references": "list",   # ["1", "2a", "3"]
        "cross_references": "list",  # ["W-2", "Schedule B"]
        "topics": "list",            # ["income", "wages"]
        "chunk_index": "int",        # Position in document
        "token_count": "int",        # Chunk size
    }


class TaxVectorDB:
    """ChromaDB wrapper for tax document retrieval."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        persist_dir = Path(self.config['chromadb']['persist_directory'])
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collections = {}
        self._init_collections()
    
    def _init_collections(self):
        """Initialize or get existing collections."""
        prefix = self.config['chromadb']['collection_prefix']
        
        for coll_key, coll_config in self.config['chromadb']['collections'].items():
            name = f"{prefix}{coll_config['name']}"
            
            self.collections[coll_key] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": coll_config['description']}
            )
            
            logger.info(f"Collection '{name}' ready ({self.collections[coll_key].count()} documents)")
    
    def get_collection(self, doc_type: str) -> chromadb.Collection:
        """Get the appropriate collection for a document type."""
        type_mapping = {
            'form': 'forms',
            'forms': 'forms',
            'instructions': 'instructions',
            'publication': 'publications',
            'publications': 'publications',
            'schedule': 'schedules',
            'schedules': 'schedules',
        }
        
        coll_key = type_mapping.get(doc_type.lower(), 'forms')
        return self.collections.get(coll_key, self.collections['forms'])
    
    def add_chunks(
        self,
        chunks: list[dict],
        doc_type: str,
        embeddings: Optional[list[list[float]]] = None
    ):
        """Add chunks to the appropriate collection."""
        collection = self.get_collection(doc_type)
        
        ids = [c['chunk_id'] for c in chunks]
        documents = [c['text'] for c in chunks]
        
        # Prepare metadata (ChromaDB requires flat structure)
        metadatas = []
        for chunk in chunks:
            meta = {
                "source_doc": chunk.get('source_doc', ''),
                "doc_type": chunk.get('doc_type', ''),
                "form_number": chunk.get('form_number', '') or '',
                "tax_year": chunk.get('tax_year', 2024),
                "section": chunk.get('section', '') or '',
                "chunk_index": chunk.get('chunk_index', 0),
                "token_count": chunk.get('token_count', 0),
                # Convert lists to comma-separated strings for ChromaDB
                "line_references": ','.join(chunk.get('line_references', [])),
                "cross_references": ','.join(chunk.get('cross_references', [])),
                "topics": ','.join(chunk.get('topics', [])),
            }
            metadatas.append(meta)
        
        # Add to collection
        if embeddings:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            # Let ChromaDB generate embeddings
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        logger.info(f"Added {len(chunks)} chunks to {collection.name}")
    
    def query(
        self,
        query_text: str,
        doc_type: Optional[str] = None,
        form_number: Optional[str] = None,
        tax_year: Optional[int] = None,
        topics: Optional[list[str]] = None,
        n_results: int = 5
    ) -> dict:
        """Query the vector database with optional filters."""
        
        # Build where clause for filtering
        where = {}
        where_conditions = []
        
        if form_number:
            where_conditions.append({"form_number": form_number})
        
        if tax_year:
            where_conditions.append({"tax_year": tax_year})
        
        if topics:
            # Match any of the topics
            for topic in topics:
                where_conditions.append({"topics": {"$contains": topic}})
        
        if len(where_conditions) == 1:
            where = where_conditions[0]
        elif len(where_conditions) > 1:
            where = {"$and": where_conditions}
        
        # Query appropriate collection(s)
        if doc_type:
            collections = [self.get_collection(doc_type)]
        else:
            collections = list(self.collections.values())
        
        all_results = {
            "ids": [],
            "documents": [],
            "metadatas": [],
            "distances": []
        }
        
        for collection in collections:
            try:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where if where else None
                )
                
                # Merge results
                if results['ids'] and results['ids'][0]:
                    all_results['ids'].extend(results['ids'][0])
                    all_results['documents'].extend(results['documents'][0])
                    all_results['metadatas'].extend(results['metadatas'][0])
                    all_results['distances'].extend(results['distances'][0])
            except Exception as e:
                logger.warning(f"Query failed for {collection.name}: {e}")
        
        # Sort by distance and limit
        if all_results['ids']:
            combined = list(zip(
                all_results['distances'],
                all_results['ids'],
                all_results['documents'],
                all_results['metadatas']
            ))
            combined.sort(key=lambda x: x[0])
            combined = combined[:n_results]
            
            all_results = {
                "ids": [c[1] for c in combined],
                "documents": [c[2] for c in combined],
                "metadatas": [c[3] for c in combined],
                "distances": [c[0] for c in combined]
            }
        
        return all_results
    
    def get_stats(self) -> dict:
        """Get statistics about the database."""
        stats = {}
        
        for key, collection in self.collections.items():
            stats[key] = {
                "name": collection.name,
                "count": collection.count()
            }
        
        return stats
    
    def reset(self):
        """Reset all collections (use with caution!)."""
        for key in list(self.collections.keys()):
            collection = self.collections[key]
            self.client.delete_collection(collection.name)
        
        self.collections = {}
        self._init_collections()
        logger.warning("All collections have been reset")


def main():
    """Test database connection and show stats."""
    db = TaxVectorDB()
    
    print("\n=== TAX VECTOR DATABASE ===\n")
    
    stats = db.get_stats()
    for key, info in stats.items():
        print(f"{key}: {info['count']} documents in '{info['name']}'")


if __name__ == "__main__":
    main()
