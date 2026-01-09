"""
ChromaDB Loader

Loads processed chunks into ChromaDB collections.
"""

import json
import logging
from pathlib import Path
from tqdm import tqdm

import yaml

from .schema import TaxVectorDB

logger = logging.getLogger(__name__)


class TaxDocumentLoader:
    """Loads tax document chunks into ChromaDB."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.chunks_dir = Path(self.config['paths']['chunks'])
        self.db = TaxVectorDB(config_path)
        self.batch_size = self.config['embedding'].get('batch_size', 100)
    
    def load_document_chunks(self, doc_dir: Path) -> list[dict]:
        """Load all chunks from a document directory."""
        chunks = []
        
        manifest_path = doc_dir / "manifest.json"
        if not manifest_path.exists():
            logger.warning(f"No manifest found in {doc_dir}")
            return chunks
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        for chunk_id in manifest['chunks']:
            meta_path = doc_dir / f"{chunk_id}.json"
            
            if meta_path.exists():
                with open(meta_path) as f:
                    chunk_data = json.load(f)
                    chunks.append(chunk_data)
            else:
                logger.warning(f"Missing chunk metadata: {meta_path}")
        
        return chunks
    
    def load_all(self):
        """Load all chunks into ChromaDB."""
        # Find all document directories
        doc_dirs = [d for d in self.chunks_dir.iterdir() if d.is_dir()]
        
        logger.info(f"Found {len(doc_dirs)} document directories")
        
        total_chunks = 0
        
        for doc_dir in tqdm(doc_dirs, desc="Loading documents"):
            chunks = self.load_document_chunks(doc_dir)
            
            if not chunks:
                continue
            
            # Group chunks by doc_type
            chunks_by_type = {}
            for chunk in chunks:
                doc_type = chunk.get('doc_type', 'form')
                if doc_type not in chunks_by_type:
                    chunks_by_type[doc_type] = []
                chunks_by_type[doc_type].append(chunk)
            
            # Load each group into appropriate collection
            for doc_type, type_chunks in chunks_by_type.items():
                # Batch the loading
                for i in range(0, len(type_chunks), self.batch_size):
                    batch = type_chunks[i:i + self.batch_size]
                    self.db.add_chunks(batch, doc_type)
                
                total_chunks += len(type_chunks)
        
        print(f"\n✓ Loaded {total_chunks} chunks into ChromaDB")
        
        # Show final stats
        stats = self.db.get_stats()
        print("\nCollection counts:")
        for key, info in stats.items():
            print(f"  {key}: {info['count']}")
    
    def load_single_document(self, doc_name: str):
        """Load chunks from a single document."""
        doc_dir = self.chunks_dir / doc_name.replace('.txt', '').replace('.pdf', '')
        
        if not doc_dir.exists():
            logger.error(f"Document directory not found: {doc_dir}")
            return
        
        chunks = self.load_document_chunks(doc_dir)
        
        if not chunks:
            logger.warning(f"No chunks found for {doc_name}")
            return
        
        doc_type = chunks[0].get('doc_type', 'form')
        self.db.add_chunks(chunks, doc_type)
        
        print(f"✓ Loaded {len(chunks)} chunks from {doc_name}")


def main():
    """Main entry point."""
    loader = TaxDocumentLoader()
    loader.load_all()


if __name__ == "__main__":
    main()
