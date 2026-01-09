"""
PDF Processor

Extracts text from IRS PDF documents while preserving structure,
tables, and form references.
"""

import logging
import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of PDF text extraction."""
    source_file: str
    pages: int
    total_chars: int
    method: str
    quality_score: float
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    errors: list[str] = field(default_factory=list)


@dataclass
class ExtractedDocument:
    """Represents an extracted PDF document."""
    source: str
    doc_type: str  # form, instructions, publication
    form_number: Optional[str]
    tax_year: int
    pages: list[str]
    metadata: dict
    extraction_result: ExtractionResult


class PDFProcessor:
    """Extracts text from IRS PDF documents."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.input_dir = Path(self.config['paths']['raw_pdfs'])
        self.output_dir = Path(self.config['paths']['processed_text'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect available extraction tools
        self._init_extractors()
    
    def _init_extractors(self):
        """Initialize available PDF extraction tools."""
        self.extractors = []
        
        try:
            import pdfplumber
            self.extractors.append(('pdfplumber', self._extract_with_pdfplumber))
            logger.info("pdfplumber available")
        except ImportError:
            pass
        
        try:
            import fitz  # PyMuPDF
            self.extractors.append(('pymupdf', self._extract_with_pymupdf))
            logger.info("PyMuPDF available")
        except ImportError:
            pass
        
        if not self.extractors:
            raise RuntimeError("No PDF extraction libraries available. Install pdfplumber or PyMuPDF.")
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> tuple[list[str], dict]:
        """Extract text using pdfplumber (best for tables)."""
        import pdfplumber
        
        pages = []
        tables_found = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                
                # Extract tables separately
                tables = page.extract_tables()
                if tables:
                    tables_found += len(tables)
                    for table in tables:
                        text += "\n\n[TABLE]\n"
                        for row in table:
                            text += " | ".join(str(cell or "") for cell in row) + "\n"
                        text += "[/TABLE]\n"
                
                pages.append(text)
        
        return pages, {"tables_extracted": tables_found}
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> tuple[list[str], dict]:
        """Extract text using PyMuPDF (fast, good for text-heavy docs)."""
        import fitz
        
        pages = []
        
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                pages.append(text)
        
        return pages, {}
    
    def _detect_doc_type(self, filename: str) -> tuple[str, Optional[str]]:
        """Detect document type and form number from filename."""
        name = filename.lower().replace('.pdf', '')
        
        if name.startswith('f'):
            # Form: f1040, f8889, f1040sa
            form_num = name[1:]
            return 'form', form_num
        elif name.startswith('i'):
            # Instructions: i1040, i8889
            form_num = name[1:]
            return 'instructions', form_num
        elif name.startswith('p'):
            # Publication: p17, p590a
            pub_num = name[1:]
            return 'publication', pub_num
        else:
            return 'unknown', None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        
        # Normalize line references
        text = re.sub(r'[Ll]ine\s+(\d+)', r'Line \1', text)
        
        return text.strip()
    
    def _calculate_quality_score(
        self, 
        pages: list[str], 
        expected_pages: Optional[int] = None
    ) -> float:
        """Calculate extraction quality score."""
        if not pages:
            return 0.0
        
        score = 1.0
        
        # Check for empty pages
        empty_pages = sum(1 for p in pages if len(p.strip()) < 50)
        if empty_pages > 0:
            score -= (empty_pages / len(pages)) * 0.3
        
        # Check for garbled text (high ratio of non-ASCII)
        total_text = ''.join(pages)
        non_ascii = sum(1 for c in total_text if ord(c) > 127)
        if len(total_text) > 0:
            non_ascii_ratio = non_ascii / len(total_text)
            if non_ascii_ratio > 0.1:
                score -= 0.2
        
        # Check page count if expected
        if expected_pages and len(pages) != expected_pages:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def process_pdf(self, pdf_path: Path) -> ExtractedDocument:
        """Process a single PDF file."""
        logger.info(f"Processing: {pdf_path.name}")
        
        doc_type, form_number = self._detect_doc_type(pdf_path.name)
        
        # Try extractors in order
        pages = []
        method = ""
        extra_metadata = {}
        errors = []
        
        for extractor_name, extractor_func in self.extractors:
            try:
                pages, extra_metadata = extractor_func(pdf_path)
                method = extractor_name
                break
            except Exception as e:
                errors.append(f"{extractor_name}: {str(e)}")
                continue
        
        if not pages:
            raise RuntimeError(f"All extractors failed for {pdf_path.name}: {errors}")
        
        # Clean pages
        pages = [self._clean_text(p) for p in pages]
        
        # Calculate quality
        quality = self._calculate_quality_score(pages)
        
        # Build result
        result = ExtractionResult(
            source_file=pdf_path.name,
            pages=len(pages),
            total_chars=sum(len(p) for p in pages),
            method=method,
            quality_score=quality,
            errors=errors
        )
        
        return ExtractedDocument(
            source=pdf_path.name,
            doc_type=doc_type,
            form_number=form_number,
            tax_year=self.config['tax_year'],
            pages=pages,
            metadata=extra_metadata,
            extraction_result=result
        )
    
    def save_extracted(self, doc: ExtractedDocument):
        """Save extracted document to disk."""
        base_name = doc.source.replace('.pdf', '')
        
        # Save full text
        text_path = self.output_dir / f"{base_name}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"---\n")
            f.write(f"source: {doc.source}\n")
            f.write(f"doc_type: {doc.doc_type}\n")
            f.write(f"form_number: {doc.form_number}\n")
            f.write(f"tax_year: {doc.tax_year}\n")
            f.write(f"pages: {len(doc.pages)}\n")
            f.write(f"extracted: {doc.extraction_result.extracted_at}\n")
            f.write(f"method: {doc.extraction_result.method}\n")
            f.write(f"quality_score: {doc.extraction_result.quality_score:.2f}\n")
            f.write(f"---\n\n")
            
            # Write pages
            for i, page in enumerate(doc.pages, 1):
                f.write(f"=== PAGE {i} ===\n\n")
                f.write(page)
                f.write("\n\n")
        
        # Save metadata JSON
        meta_path = self.output_dir / f"{base_name}.json"
        with open(meta_path, 'w') as f:
            json.dump({
                "source": doc.source,
                "doc_type": doc.doc_type,
                "form_number": doc.form_number,
                "tax_year": doc.tax_year,
                "page_count": len(doc.pages),
                "total_chars": doc.extraction_result.total_chars,
                "extraction": {
                    "method": doc.extraction_result.method,
                    "quality_score": doc.extraction_result.quality_score,
                    "timestamp": doc.extraction_result.extracted_at,
                    "errors": doc.extraction_result.errors
                },
                "metadata": doc.metadata
            }, f, indent=2)
        
        logger.info(f"Saved: {text_path.name} ({doc.extraction_result.total_chars:,} chars)")
    
    def process_all(self):
        """Process all PDFs in input directory."""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        
        for pdf_path in pdf_files:
            try:
                doc = self.process_pdf(pdf_path)
                self.save_extracted(doc)
                results.append(doc.extraction_result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {e}")
                results.append(ExtractionResult(
                    source_file=pdf_path.name,
                    pages=0,
                    total_chars=0,
                    method="failed",
                    quality_score=0.0,
                    errors=[str(e)]
                ))
        
        self._print_summary(results)
        return results
    
    def _print_summary(self, results: list[ExtractionResult]):
        """Print processing summary."""
        print("\n" + "=" * 50)
        print("PDF PROCESSING SUMMARY")
        print("=" * 50)
        
        successful = [r for r in results if r.quality_score > 0]
        failed = [r for r in results if r.quality_score == 0]
        
        print(f"\nProcessed: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            total_pages = sum(r.pages for r in successful)
            total_chars = sum(r.total_chars for r in successful)
            avg_quality = sum(r.quality_score for r in successful) / len(successful)
            
            print(f"Total pages: {total_pages:,}")
            print(f"Total characters: {total_chars:,}")
            print(f"Average quality: {avg_quality:.2f}")
        
        if failed:
            print("\nFailed files:")
            for r in failed:
                print(f"  - {r.source_file}: {r.errors}")


def main():
    """Main entry point."""
    processor = PDFProcessor()
    processor.process_all()


if __name__ == "__main__":
    main()
