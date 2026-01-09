"""
Tax Document Chunker

Performs semantic chunking of tax documents optimized for RAG retrieval.
Preserves form line references, keeps related content together.
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import hashlib

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk for embedding."""
    chunk_id: str
    text: str
    source_doc: str
    doc_type: str
    form_number: Optional[str]
    tax_year: int
    
    # Location
    page_numbers: list[int] = field(default_factory=list)
    section: Optional[str] = None
    
    # Tax-specific
    line_references: list[str] = field(default_factory=list)
    cross_references: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    
    # Chunking metadata
    chunk_index: int = 0
    token_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source_doc": self.source_doc,
            "doc_type": self.doc_type,
            "form_number": self.form_number,
            "tax_year": self.tax_year,
            "page_numbers": self.page_numbers,
            "section": self.section,
            "line_references": self.line_references,
            "cross_references": self.cross_references,
            "topics": self.topics,
            "chunk_index": self.chunk_index,
            "token_count": self.token_count
        }


class TaxDocumentChunker:
    """Chunks tax documents with semantic awareness."""
    
    # Patterns for detecting section boundaries
    SECTION_PATTERNS = [
        r'^(?:Part|PART)\s+([IVX]+)',          # Part I, Part II
        r'^(?:Section|SECTION)\s+(\d+)',       # Section 1, Section 2
        r'^(?:Schedule|SCHEDULE)\s+([A-Z])',   # Schedule A, Schedule B
        r'^(?:Chapter|CHAPTER)\s+(\d+)',       # Chapter 1
        r'^(?:Line|LINE)\s+(\d+[a-z]?)\.',     # Line 1., Line 2a.
    ]
    
    # Patterns for line references
    LINE_PATTERNS = [
        r'[Ll]ine\s+(\d+[a-z]?)',
        r'[Ll]ines\s+(\d+)\s*(?:through|to|-)\s*(\d+)',
        r'[Bb]ox\s+(\d+)',
    ]
    
    # Patterns for cross-references
    XREF_PATTERNS = [
        r'[Ff]orm\s+(\d{4}[A-Z]?)',
        r'[Ss]chedule\s+([A-Z])',
        r'[Pp]ublication\s+(\d+)',
        r'[Pp]ub\.?\s*(\d+)',
        r'W-2',
        r'1099-[A-Z]+',
    ]
    
    # Topic keywords
    TOPIC_KEYWORDS = {
        'income': ['wages', 'salary', 'income', 'earnings', 'compensation', 'w-2'],
        'deductions': ['deduct', 'itemize', 'standard deduction', 'expense'],
        'credits': ['credit', 'refundable', 'nonrefundable', 'eic', 'child tax'],
        'retirement': ['ira', '401k', 'pension', 'distribution', 'rollover', 'rmd'],
        'healthcare': ['hsa', 'insurance', 'premium', 'aca', 'marketplace', 'medical'],
        'self_employment': ['self-employed', 'schedule c', 'business', '1099-nec'],
        'capital_gains': ['capital gain', 'stock', 'sale', 'basis', '1099-b'],
        'dependents': ['dependent', 'child', 'qualifying', 'custody'],
        'filing_status': ['single', 'married', 'head of household', 'mfj', 'mfs'],
    }
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.input_dir = Path(self.config['paths']['processed_text'])
        self.output_dir = Path(self.config['paths']['chunks'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load tokenizer for counting
        try:
            import tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            logger.warning("tiktoken not available, using approximate token counting")
            self.tokenizer = None
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Approximate: ~4 chars per token
        return len(text) // 4
    
    def _generate_chunk_id(self, source: str, index: int, text: str) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{source}_{index}_{text[:100]}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        base_name = source.replace('.txt', '').replace('.pdf', '')
        return f"{base_name}_chunk_{index:04d}_{short_hash}"
    
    def _extract_line_references(self, text: str) -> list[str]:
        """Extract all line number references from text."""
        lines = set()
        
        for pattern in self.LINE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                groups = match.groups()
                if len(groups) == 1:
                    lines.add(groups[0])
                elif len(groups) == 2:
                    # Range: lines 1-5
                    try:
                        start, end = int(groups[0]), int(groups[1])
                        for i in range(start, end + 1):
                            lines.add(str(i))
                    except ValueError:
                        lines.add(groups[0])
        
        return sorted(lines, key=lambda x: (int(re.search(r'\d+', x).group()), x))
    
    def _extract_cross_references(self, text: str) -> list[str]:
        """Extract references to other IRS documents."""
        refs = set()
        
        for pattern in self.XREF_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                refs.add(match.group(0))
        
        return sorted(refs)
    
    def _extract_topics(self, text: str) -> list[str]:
        """Classify text by tax topics."""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    topics.append(topic)
                    break
        
        return topics
    
    def _detect_section(self, text: str) -> Optional[str]:
        """Detect section header in text."""
        for pattern in self.SECTION_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(0)
        return None
    
    def _find_split_points(self, text: str) -> list[int]:
        """Find optimal split points in text."""
        split_points = [0]
        
        # Priority 1: Section headers
        for pattern in self.SECTION_PATTERNS:
            for match in re.finditer(pattern, text, re.MULTILINE):
                split_points.append(match.start())
        
        # Priority 2: Double newlines (paragraph breaks)
        for match in re.finditer(r'\n\n+', text):
            split_points.append(match.start())
        
        # Priority 3: Single newlines (if needed)
        for match in re.finditer(r'\n', text):
            split_points.append(match.start())
        
        split_points.append(len(text))
        return sorted(set(split_points))
    
    def _should_preserve_intact(self, text: str) -> bool:
        """Check if text should be kept as single chunk."""
        # Preserve tax tables
        if '[TABLE]' in text or 'If taxable income is' in text:
            return True
        
        # Preserve worksheets
        if 'Worksheet' in text and len(text) < 3000:
            return True
        
        # Preserve examples
        if text.strip().startswith('Example') and len(text) < 2000:
            return True
        
        return False
    
    def chunk_document(
        self, 
        text: str, 
        source: str,
        doc_type: str,
        form_number: Optional[str],
        tax_year: int
    ) -> list[Chunk]:
        """Chunk a document into retrieval-optimized pieces."""
        
        # Get chunking config for this doc type
        chunk_config = self.config['chunking'].get(
            doc_type, 
            self.config['chunking']['default']
        )
        target_tokens = chunk_config['target_tokens']
        max_tokens = chunk_config['max_tokens']
        overlap_tokens = chunk_config['overlap_tokens']
        
        chunks = []
        split_points = self._find_split_points(text)
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, split_point in enumerate(split_points[1:], 1):
            segment = text[split_points[i-1]:split_point]
            
            # Check if segment should be preserved intact
            if self._should_preserve_intact(segment):
                # Save current chunk if exists
                if current_chunk.strip():
                    chunks.append(self._create_chunk(
                        text=current_chunk,
                        source=source,
                        doc_type=doc_type,
                        form_number=form_number,
                        tax_year=tax_year,
                        chunk_index=chunk_index
                    ))
                    chunk_index += 1
                
                # Add preserved segment as own chunk
                chunks.append(self._create_chunk(
                    text=segment,
                    source=source,
                    doc_type=doc_type,
                    form_number=form_number,
                    tax_year=tax_year,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                current_chunk = ""
                continue
            
            # Add segment to current chunk
            potential_chunk = current_chunk + segment
            potential_tokens = self._count_tokens(potential_chunk)
            
            if potential_tokens > max_tokens and current_chunk.strip():
                # Save current chunk
                chunks.append(self._create_chunk(
                    text=current_chunk,
                    source=source,
                    doc_type=doc_type,
                    form_number=form_number,
                    tax_year=tax_year,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk, overlap_tokens)
                current_chunk = overlap_text + segment
            else:
                current_chunk = potential_chunk
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(
                text=current_chunk,
                source=source,
                doc_type=doc_type,
                form_number=form_number,
                tax_year=tax_year,
                chunk_index=chunk_index
            ))
        
        return chunks
    
    def _get_overlap(self, text: str, overlap_tokens: int) -> str:
        """Get overlap text from end of chunk."""
        if self.tokenizer:
            tokens = self.tokenizer.encode(text)
            if len(tokens) > overlap_tokens:
                overlap_tokens_list = tokens[-overlap_tokens:]
                return self.tokenizer.decode(overlap_tokens_list)
        
        # Approximate: last N*4 characters
        chars = overlap_tokens * 4
        return text[-chars:] if len(text) > chars else text
    
    def _create_chunk(
        self,
        text: str,
        source: str,
        doc_type: str,
        form_number: Optional[str],
        tax_year: int,
        chunk_index: int
    ) -> Chunk:
        """Create a Chunk object with extracted metadata."""
        return Chunk(
            chunk_id=self._generate_chunk_id(source, chunk_index, text),
            text=text.strip(),
            source_doc=source,
            doc_type=doc_type,
            form_number=form_number,
            tax_year=tax_year,
            section=self._detect_section(text),
            line_references=self._extract_line_references(text),
            cross_references=self._extract_cross_references(text),
            topics=self._extract_topics(text),
            chunk_index=chunk_index,
            token_count=self._count_tokens(text)
        )
    
    def process_file(self, text_path: Path) -> list[Chunk]:
        """Process a single extracted text file."""
        logger.info(f"Chunking: {text_path.name}")
        
        # Read text file
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse header
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                header = parts[1]
                text = parts[2]
                
                # Extract metadata from header
                doc_type = re.search(r'doc_type:\s*(\w+)', header)
                form_number = re.search(r'form_number:\s*(\S+)', header)
                tax_year = re.search(r'tax_year:\s*(\d+)', header)
                
                doc_type = doc_type.group(1) if doc_type else 'unknown'
                form_number = form_number.group(1) if form_number else None
                tax_year = int(tax_year.group(1)) if tax_year else self.config['tax_year']
            else:
                text = content
                doc_type = 'unknown'
                form_number = None
                tax_year = self.config['tax_year']
        else:
            text = content
            doc_type = 'unknown'
            form_number = None
            tax_year = self.config['tax_year']
        
        # Chunk the document
        chunks = self.chunk_document(
            text=text,
            source=text_path.name,
            doc_type=doc_type,
            form_number=form_number,
            tax_year=tax_year
        )
        
        return chunks
    
    def save_chunks(self, chunks: list[Chunk], source_name: str):
        """Save chunks to disk."""
        doc_dir = self.output_dir / source_name.replace('.txt', '')
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Save manifest
        manifest = {
            "source": source_name,
            "total_chunks": len(chunks),
            "chunks": [c.chunk_id for c in chunks]
        }
        with open(doc_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Save individual chunks
        for chunk in chunks:
            # Save text
            text_path = doc_dir / f"{chunk.chunk_id}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(chunk.text)
            
            # Save metadata
            meta_path = doc_dir / f"{chunk.chunk_id}.json"
            with open(meta_path, 'w') as f:
                json.dump(chunk.to_dict(), f, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks for {source_name}")
    
    def process_all(self):
        """Process all extracted text files."""
        text_files = list(self.input_dir.glob("*.txt"))
        logger.info(f"Found {len(text_files)} text files to chunk")
        
        total_chunks = 0
        
        for text_path in text_files:
            try:
                chunks = self.process_file(text_path)
                self.save_chunks(chunks, text_path.name)
                total_chunks += len(chunks)
            except Exception as e:
                logger.error(f"Failed to chunk {text_path.name}: {e}")
        
        print(f"\n✓ Created {total_chunks} chunks from {len(text_files)} documents")


def main():
    """Main entry point."""
    chunker = TaxDocumentChunker()
    chunker.process_all()


if __name__ == "__main__":
    main()
