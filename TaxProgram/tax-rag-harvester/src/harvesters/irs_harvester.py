"""
IRS Document Harvester

Downloads tax forms, instructions, and publications from IRS.gov
with proper rate limiting and error handling.
"""

import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

import httpx
import yaml
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result of a document download attempt."""
    url: str
    filename: str
    success: bool
    file_size: int = 0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DocumentCatalog:
    """Tracks downloaded documents and their metadata."""
    documents: dict = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add(self, doc_type: str, doc_id: str, result: DownloadResult):
        if doc_type not in self.documents:
            self.documents[doc_type] = {}
        self.documents[doc_type][doc_id] = {
            "url": result.url,
            "filename": result.filename,
            "file_size": result.file_size,
            "downloaded": result.timestamp,
            "success": result.success,
            "error": result.error
        }
        self.last_updated = datetime.now().isoformat()
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump({
                "documents": self.documents,
                "last_updated": self.last_updated
            }, f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> "DocumentCatalog":
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data)
        return cls()


class IRSHarvester:
    """Downloads tax documents from IRS.gov."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.base_url = self.config['irs']['base_url']
        self.rate_limit = self.config['irs']['rate_limit']
        self.output_dir = Path(self.config['paths']['raw_pdfs'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.catalog = DocumentCatalog.load(Path(self.config['paths']['catalog']))
        self._last_request = 0.0
    
    async def _rate_limit(self):
        """Enforce rate limiting between requests."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request
        delay = 1.0 / self.rate_limit
        
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)
        
        self._last_request = asyncio.get_event_loop().time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _download_file(
        self, 
        client: httpx.AsyncClient, 
        url: str, 
        output_path: Path
    ) -> DownloadResult:
        """Download a single file with retry logic."""
        await self._rate_limit()
        
        try:
            response = await client.get(url, follow_redirects=True)
            
            if response.status_code == 404:
                return DownloadResult(
                    url=url,
                    filename=output_path.name,
                    success=False,
                    error="404 Not Found"
                )
            
            response.raise_for_status()
            
            # Verify it's a PDF
            content = response.content
            if not content.startswith(b'%PDF'):
                return DownloadResult(
                    url=url,
                    filename=output_path.name,
                    success=False,
                    error="Not a valid PDF file"
                )
            
            # Save file
            output_path.write_bytes(content)
            
            return DownloadResult(
                url=url,
                filename=output_path.name,
                success=True,
                file_size=len(content)
            )
            
        except httpx.HTTPStatusError as e:
            return DownloadResult(
                url=url,
                filename=output_path.name,
                success=False,
                error=f"HTTP {e.response.status_code}"
            )
        except Exception as e:
            return DownloadResult(
                url=url,
                filename=output_path.name,
                success=False,
                error=str(e)
            )
    
    def _build_url(self, doc_type: str, doc_id: str) -> str:
        """Build IRS URL for a document."""
        if doc_type == "form":
            return f"{self.base_url}/f{doc_id}.pdf"
        elif doc_type == "instructions":
            return f"{self.base_url}/i{doc_id}.pdf"
        elif doc_type == "publication":
            return f"{self.base_url}/p{doc_id}.pdf"
        else:
            raise ValueError(f"Unknown document type: {doc_type}")
    
    async def download_forms(self, form_ids: list[str]) -> list[DownloadResult]:
        """Download multiple forms."""
        results = []
        
        async with httpx.AsyncClient(
            timeout=self.config['irs']['timeout'],
            headers={"User-Agent": self.config['irs']['user_agent']}
        ) as client:
            for form_id in tqdm(form_ids, desc="Downloading forms"):
                url = self._build_url("form", form_id)
                output_path = self.output_dir / f"f{form_id}.pdf"
                
                # Skip if already downloaded
                if output_path.exists():
                    logger.info(f"Skipping {form_id} - already exists")
                    continue
                
                result = await self._download_file(client, url, output_path)
                results.append(result)
                self.catalog.add("forms", form_id, result)
                
                if result.success:
                    logger.info(f"✓ f{form_id}.pdf ({result.file_size:,} bytes)")
                else:
                    logger.warning(f"✗ f{form_id}.pdf - {result.error}")
        
        return results
    
    async def download_instructions(self, form_ids: list[str]) -> list[DownloadResult]:
        """Download form instructions."""
        results = []
        
        async with httpx.AsyncClient(
            timeout=self.config['irs']['timeout'],
            headers={"User-Agent": self.config['irs']['user_agent']}
        ) as client:
            for form_id in tqdm(form_ids, desc="Downloading instructions"):
                url = self._build_url("instructions", form_id)
                output_path = self.output_dir / f"i{form_id}.pdf"
                
                if output_path.exists():
                    logger.info(f"Skipping i{form_id} - already exists")
                    continue
                
                result = await self._download_file(client, url, output_path)
                results.append(result)
                self.catalog.add("instructions", form_id, result)
                
                if result.success:
                    logger.info(f"✓ i{form_id}.pdf ({result.file_size:,} bytes)")
                else:
                    logger.warning(f"✗ i{form_id}.pdf - {result.error}")
        
        return results
    
    async def download_publications(self, pub_ids: list[str]) -> list[DownloadResult]:
        """Download IRS publications."""
        results = []
        
        async with httpx.AsyncClient(
            timeout=self.config['irs']['timeout'],
            headers={"User-Agent": self.config['irs']['user_agent']}
        ) as client:
            for pub_id in tqdm(pub_ids, desc="Downloading publications"):
                url = self._build_url("publication", pub_id)
                output_path = self.output_dir / f"p{pub_id}.pdf"
                
                if output_path.exists():
                    logger.info(f"Skipping p{pub_id} - already exists")
                    continue
                
                result = await self._download_file(client, url, output_path)
                results.append(result)
                self.catalog.add("publications", pub_id, result)
                
                if result.success:
                    logger.info(f"✓ p{pub_id}.pdf ({result.file_size:,} bytes)")
                else:
                    logger.warning(f"✗ p{pub_id}.pdf - {result.error}")
        
        return results
    
    async def harvest_all(self):
        """Download all configured documents."""
        logger.info("Starting IRS document harvest...")
        
        # Collect all form IDs from config
        all_forms = []
        for category in self.config['forms'].values():
            all_forms.extend(category)
        
        # Download forms
        await self.download_forms(all_forms)
        
        # Download instructions
        instructions = [i.replace('i', '') for i in self.config['instructions']]
        await self.download_instructions(instructions)
        
        # Download publications
        all_pubs = []
        for category in self.config['publications'].values():
            all_pubs.extend(category)
        # Strip 'p' prefix if present
        all_pubs = [p.replace('p', '') for p in all_pubs]
        await self.download_publications(all_pubs)
        
        # Save catalog
        self.catalog.save(Path(self.config['paths']['catalog']))
        
        logger.info("Harvest complete!")
        self._print_summary()
    
    def _print_summary(self):
        """Print download summary."""
        print("\n" + "=" * 50)
        print("HARVEST SUMMARY")
        print("=" * 50)
        
        for doc_type, docs in self.catalog.documents.items():
            successful = sum(1 for d in docs.values() if d['success'])
            failed = len(docs) - successful
            total_size = sum(d['file_size'] for d in docs.values() if d['success'])
            
            print(f"\n{doc_type.upper()}:")
            print(f"  Downloaded: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Total size: {total_size:,} bytes")


async def main():
    """Main entry point."""
    harvester = IRSHarvester()
    await harvester.harvest_all()


if __name__ == "__main__":
    asyncio.run(main())
