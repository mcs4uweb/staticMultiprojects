"""
Simple PDF Table Extraction Examples - Quick Reference

Choose the method that best fits your needs:
1. pdfplumber - RECOMMENDED for most cases
2. tabula-py - Good for complex tables
3. camelot - Best quality for bordered tables
"""

import pandas as pd
from typing import List


# =============================================================================
# EXAMPLE 1: Simple Table Extraction (pdfplumber - RECOMMENDED)
# =============================================================================
def simple_table_extraction(pdf_path: str):
    """
    Simplest way to extract tables from PDF
    Best for: Most common use cases
    """
    import pdfplumber
    
    # Open PDF
    with pdfplumber.open(pdf_path) as pdf:
        # Get first page
        first_page = pdf.pages[0]
        
        # Extract tables
        tables = first_page.extract_tables()
        
        # Convert first table to DataFrame
        if tables:
            table = tables[0]
            df = pd.DataFrame(table[1:], columns=table[0])
            
            print("First Table:")
            print(df)
            
            # Save to CSV
            df.to_csv("extracted_table.csv", index=False)
            print("\nSaved to: extracted_table.csv")
            
            return df
        else:
            print("No tables found")
            return None


# =============================================================================
# EXAMPLE 2: Extract All Tables from All Pages
# =============================================================================
def extract_all_tables(pdf_path: str) -> List[pd.DataFrame]:
    """
    Extract all tables from entire PDF
    """
    import pdfplumber
    
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, 1):
                if table:
                    # Create DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
                    
                    print(f"Page {page_num}, Table {table_num}:")
                    print(df.head())
                    print(f"Shape: {df.shape}\n")
    
    return all_tables


# =============================================================================
# EXAMPLE 3: Extract Text + Tables Together
# =============================================================================
def extract_text_and_tables(pdf_path: str):
    """
    Extract both text and tables, preserving structure
    """
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\n{'='*60}")
            print(f"PAGE {page_num}")
            print('='*60)
            
            # Extract text
            text = page.extract_text()
            print("\nTEXT:")
            print(text[:500] if text else "No text found")
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\nTABLES: Found {len(tables)} table(s)")
                for i, table in enumerate(tables, 1):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        print(f"\nTable {i}:")
                        print(df)


# =============================================================================
# EXAMPLE 4: Extract Specific Table by Position
# =============================================================================
def extract_table_by_position(pdf_path: str, page_num: int = 0, table_index: int = 0):
    """
    Extract a specific table from a specific page
    """
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf:
        if page_num < len(pdf.pages):
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if tables and table_index < len(tables):
                table = tables[table_index]
                df = pd.DataFrame(table[1:], columns=table[0])
                
                print(f"Extracted table from page {page_num + 1}, table {table_index + 1}:")
                print(df)
                return df
            else:
                print(f"Table {table_index} not found on page {page_num + 1}")
        else:
            print(f"Page {page_num + 1} not found")
    
    return None


# =============================================================================
# EXAMPLE 5: Medical Document Table Extraction (Your Use Case)
# =============================================================================
def extract_medical_data_table(pdf_path: str, save_to: str = "medical_data.csv"):
    """
    Extract medical data tables with specific formatting
    Good for: Medical reports, lab results, patient data
    """
    import pdfplumber
    
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if table and len(table) > 1:
                    # Assuming first row is header
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Clean up data
                    df = df.dropna(how='all')  # Remove empty rows
                    df = df.fillna('')  # Replace NaN with empty string
                    
                    # Clean column names
                    df.columns = df.columns.str.strip()
                    
                    all_data.append(df)
    
    if all_data:
        # Combine all tables
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"Extracted {len(all_data)} table(s)")
        print(f"Total rows: {len(combined_df)}")
        print("\nPreview:")
        print(combined_df.head(10))
        
        # Save to CSV
        combined_df.to_csv(save_to, index=False)
        print(f"\nSaved to: {save_to}")
        
        return combined_df
    else:
        print("No tables found")
        return None


# =============================================================================
# EXAMPLE 6: Extract Table with Custom Settings
# =============================================================================
def extract_table_custom_settings(pdf_path: str):
    """
    Extract tables with custom table detection settings
    Useful when default settings don't work well
    """
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        # Custom table settings
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "explicit_vertical_lines": [],
            "explicit_horizontal_lines": [],
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "min_words_vertical": 3,
            "min_words_horizontal": 1,
        }
        
        # Extract with custom settings
        tables = page.extract_tables(table_settings=table_settings)
        
        if tables:
            df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
            print("Extracted table with custom settings:")
            print(df)
            return df
        else:
            print("No tables found")
            return None


# =============================================================================
# EXAMPLE 7: Save Multiple Tables to Excel (Different Sheets)
# =============================================================================
def save_tables_to_excel(pdf_path: str, output_excel: str = "tables.xlsx"):
    """
    Extract all tables and save to Excel with multiple sheets
    """
    import pdfplumber
    
    all_tables = []
    
    # Extract all tables
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, 1):
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append({
                        'page': page_num,
                        'table': table_num,
                        'data': df
                    })
    
    # Save to Excel
    if all_tables:
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            for item in all_tables:
                sheet_name = f"P{item['page']}_T{item['table']}"
                item['data'].to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"Saved {len(all_tables)} tables to: {output_excel}")
        return True
    else:
        print("No tables found")
        return False


# =============================================================================
# EXAMPLE 8: Extract and Filter Tables by Content
# =============================================================================
def extract_tables_with_keyword(pdf_path: str, keyword: str):
    """
    Extract only tables that contain a specific keyword
    Useful for: Finding specific data tables in large PDFs
    """
    import pdfplumber
    
    matching_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, 1):
                if table:
                    # Check if keyword is in table
                    table_str = str(table)
                    if keyword.lower() in table_str.lower():
                        df = pd.DataFrame(table[1:], columns=table[0])
                        matching_tables.append({
                            'page': page_num,
                            'table': table_num,
                            'data': df
                        })
                        
                        print(f"Found '{keyword}' in page {page_num}, table {table_num}")
                        print(df)
                        print()
    
    print(f"\nTotal tables with '{keyword}': {len(matching_tables)}")
    return matching_tables


# =============================================================================
# QUICK START DEMO
# =============================================================================
if __name__ == "__main__":
    import sys
    
    print("PDF Table Extraction - Simple Examples")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "quote.pdf"
        print(f"Usage: python {sys.argv[0]} <pdf_file>")
        print(f"Using default: {pdf_path}\n")
    
    try:
        # Example 1: Simple extraction
        print("\n1. Simple Table Extraction:")
        print("-" * 60)
        simple_table_extraction(pdf_path)
        
        # Example 2: Extract all tables
        print("\n2. Extract All Tables:")
        print("-" * 60)
        all_tables = extract_all_tables(pdf_path)
        print(f"Total tables extracted: {len(all_tables)}")
        
        # Example 7: Save to Excel
        print("\n3. Save to Excel:")
        print("-" * 60)
        save_tables_to_excel(pdf_path, "output_tables.xlsx")
        
    except FileNotFoundError:
        print(f"\nError: PDF file not found: {pdf_path}")
        print("\nCreate a test PDF or specify an existing PDF:")
        print(f"  python {sys.argv[0]} your_document.pdf")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure pdfplumber is installed:")
        print("  pip install pdfplumber --break-system-packages")
