# US Tax Filing RAG System

A document harvesting and retrieval system for US tax forms, instructions, and publications using ChromaDB.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Harvesting Pipeline                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  IRS Forms      │  Instructions   │  Publications               │
│  (f*.pdf)       │  (i*.pdf)       │  (p*.pdf)                   │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Document Processing Pipeline                        │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐     │
│  │ PDF      │  │ Semantic     │  │ Metadata Extraction    │     │
│  │ Extract  │→ │ Chunking     │→ │ (form, year, topic)    │     │
│  └──────────┘  └──────────────┘  └────────────────────────┘     │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ChromaDB Vector Store                         │
│  Collections: forms | instructions | publications | schedules   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure (copy and edit)
cp config/settings.example.yaml config/settings.yaml

# Harvest IRS documents
python -m src.harvesters.irs_harvester

# Process and chunk documents
python -m src.processors.pdf_processor

# Load into ChromaDB
python -m src.db.loader

# Test retrieval
python -m src.db.query_test
```

## Project Structure

```
tax-rag-harvester/
├── .claude/
│   └── agents/              # Claude Code subagents
│       ├── tax-harvester.md
│       ├── pdf-processor.md
│       ├── chunk-strategist.md
│       ├── metadata-extractor.md
│       └── qa-validator.md
├── src/
│   ├── harvesters/          # Document downloaders
│   │   ├── irs_harvester.py
│   │   └── form_catalog.py
│   ├── processors/          # PDF extraction & chunking
│   │   ├── pdf_processor.py
│   │   └── chunker.py
│   ├── db/                  # ChromaDB operations
│   │   ├── schema.py
│   │   ├── loader.py
│   │   └── query_test.py
│   └── utils/
│       ├── rate_limiter.py
│       └── text_cleaner.py
├── config/
│   └── settings.yaml
├── data/
│   ├── raw/                 # Downloaded PDFs
│   └── processed/           # Extracted text/chunks
└── tests/
```

## Key Data Sources

| Source | URL Pattern | Content |
|--------|-------------|---------|
| Forms | `irs.gov/pub/irs-pdf/fXXXX.pdf` | Fillable tax forms |
| Instructions | `irs.gov/pub/irs-pdf/iXXXX.pdf` | Form instructions |
| Publications | `irs.gov/pub/irs-pdf/pXXX.pdf` | Tax guidance |
| Schedules | `irs.gov/pub/irs-pdf/fXXXXsY.pdf` | Form schedules |

## Priority Forms (2024 Tax Year)

### Individual Returns
- **1040** - US Individual Income Tax Return
- **Schedule A** - Itemized Deductions
- **Schedule B** - Interest and Dividends
- **Schedule C** - Profit or Loss from Business
- **Schedule D** - Capital Gains and Losses
- **Schedule E** - Supplemental Income
- **Schedule SE** - Self-Employment Tax

### Credits & Deductions
- **8889** - Health Savings Accounts
- **8863** - Education Credits
- **5695** - Residential Energy Credits
- **2441** - Child and Dependent Care

### Retirement
- **8606** - Nondeductible IRAs
- **5329** - Additional Taxes on Qualified Plans
- **1099-R** - Distributions from Pensions

### Key Publications
- **Pub 17** - Your Federal Income Tax (comprehensive guide)
- **Pub 501** - Dependents, Standard Deduction, Filing Info
- **Pub 590-A/B** - IRAs (Contributions/Distributions)
- **Pub 969** - HSAs and Other Tax-Favored Health Plans

## ChromaDB Collections

| Collection | Content | Metadata Fields |
|------------|---------|-----------------|
| `tax_forms` | Form content | form_number, year, title, page |
| `instructions` | Form instructions | form_number, year, section, line_ref |
| `publications` | IRS publications | pub_number, year, chapter, topic |
| `schedules` | Schedule forms | parent_form, schedule_letter, year |

## Chunking Strategy

Tax documents require special chunking to preserve context:

1. **Section-aware splitting** - Keep form sections together
2. **Line number preservation** - Maintain references to specific lines
3. **Cross-reference detection** - Link related forms/schedules
4. **Table handling** - Keep tax tables intact
5. **Overlap** - 200 token overlap for context continuity

## Using with Claude Code Agents

The `.claude/agents/` directory contains specialized subagents:

```bash
# In Claude Code, use agents for parallel processing:
"Use the tax-harvester agent to download all 1040-related forms"
"Use the pdf-processor agent to extract text from the downloaded PDFs"
"Use 4 parallel chunk-strategist agents to process the extracted text"
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=your-key-here
CHROMA_PERSIST_DIR=./data/chroma
IRS_RATE_LIMIT=2  # requests per second
```

## License

MIT
