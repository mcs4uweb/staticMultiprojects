"""
PDF Text and Table Extraction Examples
Comprehensive guide for extracting text and tables from PDFs using various Python libraries

Requirements:
    pip install pypdf2 pdfplumber tabula-py camelot-py[cv] pymupdf pandas openpyxl --break-system-packages
    
Note: Some methods work better for different types of PDFs
"""

import os
from typing import List, Dict, Optional
import pandas as pd


# =============================================================================
# METHOD 1: PyPDF2 - Basic Text Extraction
# =============================================================================
def extract_text_pypdf2(pdf_path: str) -> str:
    """
    Extract text using PyPDF2 (basic method)
    Good for: Simple text extraction, no tables
    """
    try:
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"Total pages: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text += f"\n--- Page {page_num} ---\n"
                text += page.extract_text()
        
        return text
    
    except ImportError:
        return "Error: PyPDF2 not installed. Run: pip install pypdf2 --break-system-packages"
    except Exception as e:
        return f"Error extracting text: {e}"


# =============================================================================
# METHOD 2: pdfplumber - Best for Tables
# =============================================================================
def extract_tables_pdfplumber(pdf_path: str, output_dir: str = "output") -> List[pd.DataFrame]:
    """
    Extract tables using pdfplumber (RECOMMENDED for most use cases)
    Good for: Tables, mixed content, preserves structure
    """
    try:
        import pdfplumber
        
        os.makedirs(output_dir, exist_ok=True)
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\nPage {page_num}:")
                
                # Extract text
                text = page.extract_text()
                if text:
                    print(f"  Text length: {len(text)} characters")
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    print(f"  Found {len(tables)} table(s)")
                    
                    for table_num, table in enumerate(tables, 1):
                        if table:
                            # Convert to DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            all_tables.append(df)
                            
                            # Save to CSV
                            csv_filename = f"{output_dir}/page{page_num}_table{table_num}.csv"
                            df.to_csv(csv_filename, index=False)
                            print(f"    Table {table_num}: {df.shape[0]} rows x {df.shape[1]} cols")
                            print(f"    Saved to: {csv_filename}")
        
        return all_tables
    
    except ImportError:
        print("Error: pdfplumber not installed. Run: pip install pdfplumber --break-system-packages")
        return []
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []


def extract_text_and_tables_pdfplumber(pdf_path: str) -> Dict:
    """
    Extract both text and tables from each page using pdfplumber
    Returns structured data with text and tables per page
    """
    try:
        import pdfplumber
        
        result = {
            'pages': [],
            'total_pages': 0,
            'total_tables': 0
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            result['total_pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_data = {
                    'page_number': page_num,
                    'text': page.extract_text() or "",
                    'tables': []
                }
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if table and len(table) > 1:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            page_data['tables'].append(df)
                            result['total_tables'] += 1
                
                result['pages'].append(page_data)
        
        return result
    
    except Exception as e:
        return {'error': str(e)}


# =============================================================================
# METHOD 3: tabula-py - Java-based Table Extraction
# =============================================================================
def extract_tables_tabula(pdf_path: str, output_dir: str = "output") -> List[pd.DataFrame]:
    """
    Extract tables using tabula-py
    Good for: Complex tables, multi-page tables
    Requires: Java installed on system
    """
    try:
        import tabula
        
        os.makedirs(output_dir, exist_ok=True)
        
        print("Extracting tables with tabula...")
        
        # Extract all tables from all pages
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=True,
            pandas_options={'header': None}
        )
        
        print(f"Found {len(tables)} table(s)")
        
        # Save each table
        for i, df in enumerate(tables, 1):
            csv_filename = f"{output_dir}/tabula_table{i}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"Table {i}: {df.shape[0]} rows x {df.shape[1]} cols")
            print(f"  Saved to: {csv_filename}")
        
        return tables
    
    except ImportError:
        print("Error: tabula-py not installed. Run: pip install tabula-py --break-system-packages")
        print("Note: Also requires Java to be installed on your system")
        return []
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []


# =============================================================================
# METHOD 4: Camelot - High Quality Table Extraction
# =============================================================================
def extract_tables_camelot(pdf_path: str, output_dir: str = "output", 
                          flavor: str = "lattice") -> List[pd.DataFrame]:
    """
    Extract tables using Camelot (highest quality for tables)
    Good for: Perfect table extraction, form PDFs
    
    Args:
        flavor: 'lattice' (for bordered tables) or 'stream' (for borderless tables)
    """
    try:
        import camelot
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Extracting tables with Camelot ({flavor} mode)...")
        
        # Extract tables
        tables = camelot.read_pdf(pdf_path, pages='all', flavor=flavor)
        
        print(f"Found {len(tables)} table(s)")
        
        dfs = []
        for i, table in enumerate(tables, 1):
            df = table.df
            dfs.append(df)
            
            # Save to CSV
            csv_filename = f"{output_dir}/camelot_table{i}.csv"
            df.to_csv(csv_filename, index=False)
            
            # Print table info
            print(f"\nTable {i}:")
            print(f"  Accuracy: {table.accuracy}%")
            print(f"  Whitespace: {table.whitespace}%")
            print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} cols")
            print(f"  Saved to: {csv_filename}")
        
        return dfs
    
    except ImportError:
        print("Error: camelot-py not installed.")
        print("Run: pip install camelot-py[cv] --break-system-packages")
        print("Note: Also requires ghostscript to be installed on your system")
        return []
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []


# =============================================================================
# METHOD 5: PyMuPDF (fitz) - Fast and Comprehensive
# =============================================================================
def extract_text_pymupdf(pdf_path: str) -> Dict:
    """
    Extract text using PyMuPDF (fastest method)
    Good for: Large PDFs, fast processing, images
    """
    try:
        import fitz  # PyMuPDF
        
        result = {
            'pages': [],
            'metadata': {}
        }
        
        # Open PDF
        doc = fitz.open(pdf_path)
        
        # Get metadata
        result['metadata'] = doc.metadata
        result['total_pages'] = len(doc)
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            page_data = {
                'page_number': page_num + 1,
                'text': page.get_text(),
                'blocks': page.get_text("blocks"),  # Text with position info
                'words': page.get_text("words"),    # Individual words with positions
            }
            
            result['pages'].append(page_data)
        
        doc.close()
        return result
    
    except ImportError:
        return {'error': "PyMuPDF not installed. Run: pip install pymupdf --break-system-packages"}
    except Exception as e:
        return {'error': str(e)}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def save_all_tables_to_excel(tables: List[pd.DataFrame], output_file: str):
    """
    Save all extracted tables to a single Excel file with multiple sheets
    """
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for i, df in enumerate(tables, 1):
                sheet_name = f"Table_{i}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"\nSaved {len(tables)} tables to: {output_file}")
    
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def compare_extraction_methods(pdf_path: str):
    """
    Compare different extraction methods on the same PDF
    """
    print("=" * 80)
    print("COMPARING PDF EXTRACTION METHODS")
    print("=" * 80)
    
    # Method 1: PyPDF2
    print("\n1. PyPDF2 (Basic Text Extraction)")
    print("-" * 80)
    text = extract_text_pypdf2(pdf_path)
    if text and not text.startswith("Error"):
        print(f"Extracted {len(text)} characters")
        print("Preview:", text[:200], "...\n")
    else:
        print(text)
    
    # Method 2: pdfplumber
    print("\n2. pdfplumber (Text + Tables)")
    print("-" * 80)
    tables = extract_tables_pdfplumber(pdf_path, "output_pdfplumber")
    
    # Method 3: tabula
    print("\n3. tabula-py (Table Extraction)")
    print("-" * 80)
    tabula_tables = extract_tables_tabula(pdf_path, "output_tabula")
    
    # Method 4: Camelot
    print("\n4. Camelot (High Quality Tables)")
    print("-" * 80)
    camelot_tables = extract_tables_camelot(pdf_path, "output_camelot", flavor="lattice")
    
    # Method 5: PyMuPDF
    print("\n5. PyMuPDF (Fast Extraction)")
    print("-" * 80)
    pymupdf_result = extract_text_pymupdf(pdf_path)
    if 'error' not in pymupdf_result:
        print(f"Extracted {pymupdf_result['total_pages']} pages")
        print(f"Metadata: {pymupdf_result['metadata']}")
    else:
        print(pymupdf_result['error'])
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)


# =============================================================================
# MAIN DEMO
# =============================================================================
def main():
    """
    Main demonstration function
    """
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Example usage
        pdf_path = "sample.pdf"
        print(f"Usage: python {sys.argv[0]} <pdf_file>")
        print(f"\nUsing default: {pdf_path}")
        print("(Create a sample.pdf file or specify your PDF path)")
        
        if not os.path.exists(pdf_path):
            print(f"\nError: {pdf_path} not found!")
            print("\nExample usage:")
            print("  python pdf_text_table_extraction.py document.pdf")
            return
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"\nProcessing: {pdf_path}")
    print("=" * 80)
    
    # Run comparison of all methods
    compare_extraction_methods(pdf_path)


if __name__ == "__main__":
    main()
