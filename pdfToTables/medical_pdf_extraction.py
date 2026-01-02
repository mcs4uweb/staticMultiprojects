"""
Medical Document PDF Table Extraction
Specialized example for extracting data from medical PDFs like:
- Lab results
- Patient records
- Medical histories
- Test results
- Insurance forms

Usage:
    python medical_pdf_extraction.py document.pdf
"""

import pandas as pd
import pdfplumber
from typing import List, Dict, Optional
from datetime import datetime
import re
import json


class MedicalPDFExtractor:
    """Extract and process medical document data from PDFs"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = None
        
    def __enter__(self):
        self.pdf = pdfplumber.open(self.pdf_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pdf:
            self.pdf.close()
    
    def extract_patient_info(self) -> Dict:
        """
        Extract patient demographic information
        Common fields: Name, DOB, MRN, Gender, etc.
        """
        patient_info = {}
        
        if not self.pdf:
            return patient_info
        
        # Usually on first page
        first_page = self.pdf.pages[0]
        text = first_page.extract_text()
        
        if text:
            # Extract patient name (example pattern)
            name_match = re.search(r'Patient Name[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
            if name_match:
                patient_info['name'] = name_match.group(1).strip()
            
            # Extract DOB (example pattern)
            dob_match = re.search(r'(?:DOB|Date of Birth)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
            if dob_match:
                patient_info['dob'] = dob_match.group(1)
            
            # Extract MRN (Medical Record Number)
            mrn_match = re.search(r'(?:MRN|Medical Record)[:\s#]+([A-Z0-9]+)', text, re.IGNORECASE)
            if mrn_match:
                patient_info['mrn'] = mrn_match.group(1)
            
            # Extract Gender
            gender_match = re.search(r'(?:Gender|Sex)[:\s]+(Male|Female|M|F)', text, re.IGNORECASE)
            if gender_match:
                patient_info['gender'] = gender_match.group(1)
        
        return patient_info
    
    def extract_lab_results(self) -> List[Dict]:
        """
        Extract laboratory test results
        Returns list of test results with values and reference ranges
        """
        lab_results = []
        
        if not self.pdf:
            return lab_results
        
        for page in self.pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if table and len(table) > 1:
                    # Create DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Clean data
                    df = df.dropna(how='all')
                    df.columns = df.columns.str.strip()
                    
                    # Look for common lab result column patterns
                    possible_test_cols = ['Test', 'Test Name', 'Component', 'Analyte']
                    possible_value_cols = ['Result', 'Value', 'Results']
                    possible_range_cols = ['Reference Range', 'Range', 'Normal Range']
                    
                    test_col = self._find_column(df, possible_test_cols)
                    value_col = self._find_column(df, possible_value_cols)
                    range_col = self._find_column(df, possible_range_cols)
                    
                    if test_col and value_col:
                        for _, row in df.iterrows():
                            result = {
                                'test': row[test_col],
                                'value': row[value_col],
                                'range': row[range_col] if range_col else None,
                                'abnormal': self._check_if_abnormal(row)
                            }
                            lab_results.append(result)
        
        return lab_results
    
    def extract_medication_list(self) -> List[Dict]:
        """
        Extract medication information
        """
        medications = []
        
        if not self.pdf:
            return medications
        
        for page in self.pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.dropna(how='all')
                    df.columns = df.columns.str.strip()
                    
                    # Look for medication-related columns
                    med_cols = ['Medication', 'Drug', 'Medicine', 'Prescription']
                    dose_cols = ['Dose', 'Dosage', 'Strength']
                    freq_cols = ['Frequency', 'How Often', 'Schedule']
                    
                    med_col = self._find_column(df, med_cols)
                    dose_col = self._find_column(df, dose_cols)
                    freq_col = self._find_column(df, freq_cols)
                    
                    if med_col:
                        for _, row in df.iterrows():
                            med = {
                                'medication': row[med_col],
                                'dose': row[dose_col] if dose_col else None,
                                'frequency': row[freq_col] if freq_col else None
                            }
                            medications.append(med)
        
        return medications
    
    def extract_vital_signs(self) -> Dict:
        """
        Extract vital signs (BP, HR, Temp, etc.)
        """
        vitals = {}
        
        if not self.pdf:
            return vitals
        
        text = ""
        for page in self.pdf.pages:
            text += page.extract_text() or ""
        
        # Blood Pressure
        bp_match = re.search(r'(?:BP|Blood Pressure)[:\s]+(\d{2,3}/\d{2,3})', text, re.IGNORECASE)
        if bp_match:
            vitals['blood_pressure'] = bp_match.group(1)
        
        # Heart Rate
        hr_match = re.search(r'(?:HR|Heart Rate|Pulse)[:\s]+(\d{2,3})', text, re.IGNORECASE)
        if hr_match:
            vitals['heart_rate'] = hr_match.group(1)
        
        # Temperature
        temp_match = re.search(r'(?:Temp|Temperature)[:\s]+([\d.]+)', text, re.IGNORECASE)
        if temp_match:
            vitals['temperature'] = temp_match.group(1)
        
        # Weight
        weight_match = re.search(r'(?:Weight)[:\s]+([\d.]+)\s*(?:lbs?|kg)', text, re.IGNORECASE)
        if weight_match:
            vitals['weight'] = weight_match.group(1)
        
        return vitals
    
    def extract_all_tables_structured(self) -> Dict:
        """
        Extract all tables with metadata
        Returns structured data with page numbers and table positions
        """
        structured_data = {
            'document_path': self.pdf_path,
            'extracted_at': datetime.now().isoformat(),
            'total_pages': len(self.pdf.pages) if self.pdf else 0,
            'tables': []
        }
        
        if not self.pdf:
            return structured_data
        
        for page_num, page in enumerate(self.pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, 1):
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    table_info = {
                        'page': page_num,
                        'table_index': table_num,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'column_names': df.columns.tolist(),
                        'data': df.to_dict('records')
                    }
                    
                    structured_data['tables'].append(table_info)
        
        return structured_data
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Helper to find column by multiple possible names"""
        for col in df.columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _check_if_abnormal(self, row) -> bool:
        """Check if a lab result is flagged as abnormal"""
        row_str = str(row).lower()
        abnormal_flags = ['high', 'low', 'abnormal', 'critical', '*', 'h', 'l']
        return any(flag in row_str for flag in abnormal_flags)
    
    def generate_report(self, output_dir: str = "medical_extraction_output"):
        """
        Generate comprehensive extraction report
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("Extracting Medical Document Data...")
        print("=" * 60)
        
        # Extract all data
        patient_info = self.extract_patient_info()
        lab_results = self.extract_lab_results()
        medications = self.extract_medication_list()
        vitals = self.extract_vital_signs()
        all_tables = self.extract_all_tables_structured()
        
        # Print summary
        print("\nPatient Information:")
        for key, value in patient_info.items():
            print(f"  {key}: {value}")
        
        print(f"\nVital Signs:")
        for key, value in vitals.items():
            print(f"  {key}: {value}")
        
        print(f"\nLab Results: {len(lab_results)} tests found")
        if lab_results:
            abnormal_count = sum(1 for r in lab_results if r['abnormal'])
            print(f"  Abnormal results: {abnormal_count}")
        
        print(f"\nMedications: {len(medications)} found")
        
        print(f"\nTotal Tables: {len(all_tables['tables'])}")
        
        # Save data
        # 1. Patient info as JSON
        if patient_info:
            with open(f"{output_dir}/patient_info.json", 'w') as f:
                json.dump(patient_info, f, indent=2)
            print(f"\nSaved: {output_dir}/patient_info.json")
        
        # 2. Lab results as CSV
        if lab_results:
            pd.DataFrame(lab_results).to_csv(f"{output_dir}/lab_results.csv", index=False)
            print(f"Saved: {output_dir}/lab_results.csv")
        
        # 3. Medications as CSV
        if medications:
            pd.DataFrame(medications).to_csv(f"{output_dir}/medications.csv", index=False)
            print(f"Saved: {output_dir}/medications.csv")
        
        # 4. All tables as JSON
        with open(f"{output_dir}/all_tables.json", 'w') as f:
            json.dump(all_tables, f, indent=2)
        print(f"Saved: {output_dir}/all_tables.json")
        
        # 5. Full report as Excel
        with pd.ExcelWriter(f"{output_dir}/medical_report.xlsx", engine='openpyxl') as writer:
            if patient_info:
                pd.DataFrame([patient_info]).to_excel(writer, sheet_name='Patient Info', index=False)
            if lab_results:
                pd.DataFrame(lab_results).to_excel(writer, sheet_name='Lab Results', index=False)
            if medications:
                pd.DataFrame(medications).to_excel(writer, sheet_name='Medications', index=False)
            if vitals:
                pd.DataFrame([vitals]).to_excel(writer, sheet_name='Vital Signs', index=False)
        
        print(f"Saved: {output_dir}/medical_report.xlsx")
        print("\n" + "=" * 60)
        print("Extraction Complete!")


def main():
    import sys
    
    """  if len(sys.argv) < 2:
        print("Usage: python medical_pdf_extraction.py <pdf_file>")
        print("\nExample:")
        print("  python medical_pdf_extraction.py lab_results.pdf")
        return """
    
    pdf_path = "C:\Projects\python\MepcomStatic\pdfToTables\quote.pdf"
    
    try:
        with MedicalPDFExtractor(pdf_path) as extractor:
            extractor.generate_report()
    
    except FileNotFoundError:
        print(f"Error: PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
