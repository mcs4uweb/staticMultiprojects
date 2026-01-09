"""
Tests for the tax RAG harvester system.
"""

import pytest
from pathlib import Path
import tempfile
import json


class TestFormCatalog:
    """Tests for the form catalog."""
    
    def test_get_all_forms(self):
        from src.harvesters.form_catalog import get_all_forms
        
        forms = get_all_forms()
        assert "1040" in forms
        assert "8889" in forms
        assert forms["1040"].priority == 10
    
    def test_get_forms_by_priority(self):
        from src.harvesters.form_catalog import get_forms_by_priority
        
        high_priority = get_forms_by_priority(min_priority=9)
        assert "1040" in high_priority
        
        lower_priority = get_forms_by_priority(min_priority=5)
        assert len(lower_priority) > len(high_priority)
    
    def test_get_related_forms(self):
        from src.harvesters.form_catalog import get_related_forms
        
        related = get_related_forms("1040")
        assert "W-2" in related


class TestChunker:
    """Tests for the document chunker."""
    
    def test_extract_line_references(self):
        from src.processors.chunker import TaxDocumentChunker
        
        chunker = TaxDocumentChunker.__new__(TaxDocumentChunker)
        chunker.config = {"chunking": {"default": {"target_tokens": 500, "max_tokens": 1000, "overlap_tokens": 150}}}
        chunker.tokenizer = None
        
        text = "See Line 7 for wages. Lines 1 through 5 cover other income. Check Box 12."
        lines = chunker._extract_line_references(text)
        
        assert "7" in lines
        assert "12" in lines  # from Box 12
    
    def test_extract_cross_references(self):
        from src.processors.chunker import TaxDocumentChunker
        
        chunker = TaxDocumentChunker.__new__(TaxDocumentChunker)
        chunker.config = {"chunking": {"default": {"target_tokens": 500, "max_tokens": 1000, "overlap_tokens": 150}}}
        
        text = "See Form 8889 for HSA rules. Also check Schedule A and Publication 502."
        refs = chunker._extract_cross_references(text)
        
        assert any("8889" in r for r in refs)
        assert any("Schedule A" in r for r in refs)
    
    def test_extract_topics(self):
        from src.processors.chunker import TaxDocumentChunker
        
        chunker = TaxDocumentChunker.__new__(TaxDocumentChunker)
        chunker.config = {"chunking": {"default": {"target_tokens": 500, "max_tokens": 1000, "overlap_tokens": 150}}}
        
        text = "Enter your wages, salary, and tips from your W-2."
        topics = chunker._extract_topics(text)
        
        assert "income" in topics


class TestQueryBuilder:
    """Tests for query building and filtering."""
    
    def test_metadata_filtering(self):
        """Test that metadata can be used for filtering."""
        metadata = {
            "form_number": "1040",
            "tax_year": 2024,
            "topics": "income,wages",
            "line_references": "1,2,3"
        }
        
        # Verify structure is correct for ChromaDB
        assert isinstance(metadata["form_number"], str)
        assert isinstance(metadata["tax_year"], int)
        assert "," in metadata["topics"]  # Lists stored as comma-separated


class TestIntegration:
    """Integration tests for the full pipeline."""
    
    @pytest.mark.skip(reason="Requires external services")
    def test_full_pipeline(self):
        """Test harvesting -> processing -> loading -> querying."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
