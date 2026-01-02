import os
import sys
import shutil
from pathlib import Path
from typing import List, Union
import logging

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    JSONLoader,
    BSHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Optional: OCR for images
try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logging.warning("OCR not available: install 'pillow' and 'pytesseract' + Tesseract")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalIngestor:
    def __init__(
        self,
        vector_db_path: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.vector_db_path = vector_db_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        self.embedding = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = None

    def load_single_file(self, file_path: Union[str, Path]) -> List[Document]:
        """Load a single file based on its extension."""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                
                # Check if text was actually extracted
                total_text = "".join(doc.page_content for doc in docs)
                if len(total_text.strip()) > 50:  # Reasonable threshold
                    return docs
            
            elif ext in [".docx", ".doc"]:
                loader = UnstructuredWordDocumentLoader(str(file_path))
                return loader.load()
            
            elif ext == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
                return loader.load()
            
            elif ext == ".csv":
                loader = CSVLoader(str(file_path))
                return loader.load()
            
            elif ext == ".json":
                # Assumes JSON is list of dicts with "text" key
                loader = JSONLoader(
                    str(file_path),
                    jq_schema=".[] | .text",
                    text_content=False
                )
                return loader.load()
            
            elif ext in [".html", ".htm"]:
                loader = BSHTMLLoader(str(file_path))
                return loader.load()
            
            elif ext in [".md", ".markdown"]:
                loader = UnstructuredMarkdownLoader(str(file_path))
                return loader.load()
            
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"] and HAS_OCR:
                text = pytesseract.image_to_string(Image.open(file_path))
                return [Document(page_content=text, metadata={"source": str(file_path)})]
            
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return []
        
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []

    def ingest_directory(self, dir_path: Union[str, Path]):
        """Ingest all supported files in a directory."""
        dir_path = Path(dir_path)
        processed_dir = dir_path / "processed"
        processed_dir.mkdir(exist_ok=True)
        all_docs = []
        
        for file_path in dir_path.rglob("*"):
            if processed_dir in file_path.parents:
                continue
            if file_path.is_file():
                docs = self.load_single_file(file_path)
                all_docs.extend(docs)
                logger.info(f"Loaded {len(docs)} docs from {file_path}")
                self._move_to_processed(file_path, processed_dir)

        if not all_docs:
            logger.warning(f"No documents loaded from {dir_path}. Nothing to ingest.")
            return
        
        # Split documents
        splits = self.text_splitter.split_documents(all_docs)
        logger.info(f"Split into {len(splits)} chunks")
        if not splits:
            logger.warning("No chunks created after splitting. Nothing to ingest.")
            return

        # Create or update vector DB
        if not self.vectorstore:
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding,
                persist_directory=self.vector_db_path
            )
        else:
            self.vectorstore.add_documents(splits)
        
        self.vectorstore.persist()
        logger.info(f"Saved vector DB to {self.vector_db_path}")

    def _move_to_processed(self, file_path: Path, processed_dir: Path) -> None:
        target_path = processed_dir / file_path.name
        if target_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            counter = 1
            while True:
                candidate = processed_dir / f"{stem}_{counter}{suffix}"
                if not candidate.exists():
                    target_path = candidate
                    break
                counter += 1
        try:
            shutil.move(str(file_path), str(target_path))
        except Exception as e:
            logger.error(f"Failed to move {file_path} to {processed_dir}: {e}")

    def query(self, question: str, k: int = 3):
        """Query the vector DB."""
        if not self.vectorstore:
            self.vectorstore = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embedding
            )
        results = self.vectorstore.similarity_search(question, k=k)
        return results

# Example usage
if __name__ == "__main__":
    # Always use the directory where THIS script lives
    SCRIPT_DIR = Path(__file__).parent
    data_directory = SCRIPT_DIR / "data"
    if len(sys.argv) > 1:
        logger.info("Ignoring CLI args; using hard-coded 'data' directory.")
    
    if not data_directory.exists():
        logger.error(f"📁 Data directory not found: {data_directory}")
        logger.error("👉 Please create a 'data' folder next to this script and add documents.")
        sys.exit(1)
    
    ingestor = UniversalIngestor()
    ingestor.ingest_directory(data_directory)
    
    # Test query
    results = ingestor.query("Summarize the key findings")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1} (Source: {doc.metadata.get('source', 'N/A')}):\n{doc.page_content[:500]}...")
