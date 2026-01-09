import os
import logging
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pdf2image import convert_from_path
import pytesseract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxDocumentLoader(BaseLoader):
    """Specialized loader for tax documents (handles scanned PDFs)"""
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
    
    def load(self) -> List[Document]:
        try:
            # Try standard PDF text extraction first
            loader = PyPDFLoader(str(self.file_path))
            docs = loader.load()
            
            # Check if text was actually extracted
            full_text = " ".join([doc.page_content for doc in docs])
            if len(full_text.strip()) > 100:  # Reasonable threshold for tax forms
                logger.info(f"✅ Extracted text from {self.file_path.name}")
                return self._add_metadata(docs)
            
            # Fallback to OCR for scanned documents
            logger.warning(f"⚠️  Low text detected - applying OCR to {self.file_path.name}")
            return self._ocr_extract()
            
        except Exception as e:
            logger.error(f"❌ Failed to load {self.file_path}: {e}")
            return []
    
    def _ocr_extract(self) -> List[Document]:
        """Extract text from scanned PDF using OCR"""
        try:
            images = convert_from_path(str(self.file_path))
            full_text = ""
            
            for i, image in enumerate(images):
                # Optimize OCR for tax forms (dense text, tables)
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,()$-/"'
                text = pytesseract.image_to_string(image, config=custom_config)
                full_text += f"\n--- Page {i+1} ---\n{text}"
            
            doc = Document(
                page_content=full_text,
                metadata={
                    "source": str(self.file_path),
                    "file_type": self._get_form_type(self.file_path.name)
                }
            )
            return [doc]
            
        except Exception as e:
            logger.error(f"OCR failed for {self.file_path}: {e}")
            return []
    
    def _add_metadata(self, docs: List[Document]) -> List[Document]:
        """Add tax form type to metadata"""
        form_type = self._get_form_type(self.file_path.name)
        for doc in docs:
            doc.metadata["file_type"] = form_type
        return docs
    
    def _get_form_type(self, filename: str) -> str:
        """Identify tax form type from filename"""
        name_lower = filename.lower()
        if "w2" in name_lower:
            return "W-2"
        elif "schedulea" in name_lower:
            return "Schedule A"
        elif "1099-int" in name_lower:
            return "1099-INT"
        elif "1099-misc" in name_lower:
            return "1099-MISC"
        else:
            return "Unknown Tax Form"

class TaxIngestor:
    def __init__(self, data_dir: str = "data", persist_dir: str = "chroma_db"):
        base_dir = Path(__file__).resolve().parent
        data_path = Path(data_dir)
        if not data_path.is_absolute():
            data_path = base_dir / data_path
        self.data_dir = data_path

        persist_path = Path(persist_dir)
        if not persist_path.is_absolute():
            persist_path = base_dir / persist_path
        self.persist_dir = persist_path
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def ingest(self):
        """Ingest all tax documents in data_dir"""
        if not self.data_dir.exists():
            raise ValueError(f"Data directory {self.data_dir} not found")
        
        all_docs = []
        for file_path in self.data_dir.glob("*.pdf"):
            logger.info(f"Processing {file_path.name}")
            loader = TaxDocumentLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
        
        if not all_docs:
            raise ValueError("No documents loaded! Check your data directory.")
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=all_docs,
            embedding=self.embedding,
            persist_directory=str(self.persist_dir)
        )
        vectorstore.persist()
        logger.info(f"✅ Ingested {len(all_docs)} documents to {self.persist_dir}")

# For direct script execution
if __name__ == "__main__":
    ingestor = TaxIngestor()
    ingestor.ingest()
