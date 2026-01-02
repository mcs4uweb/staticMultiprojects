# PDF Text and Table Extraction with Python

Comprehensive examples for extracting text and tables from PDF documents using Python.

## 📚 Overview

This collection includes multiple approaches for PDF extraction:
- **Simple text extraction**
- **Table extraction and parsing**
- **Medical document processing**
- **Batch processing**
- **Excel/CSV export**

## 🚀 Quick Start

### Installation

```bash
# Install basic requirements
pip install pdfplumber pandas openpyxl --break-system-packages

# For all features (includes tabula and camelot)
pip install -r requirements_pdf.txt --break-system-packages
```

### Simplest Example

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    first_page = pdf.pages[0]
    
    # Extract text
    text = first_page.extract_text()
    print(text)
    
    # Extract tables
    tables = first_page.extract_tables()
    if tables:
        import pandas as pd
        df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
        print(df)
```

### Command Line Usage

```bash
# Simple extraction
python pdf_simple_examples.py your_document.pdf

# Compare all methods
python pdf_text_table_extraction.py your_document.pdf

# Medical document extraction
python medical_pdf_extraction.py lab_results.pdf
```

## 📦 Files Included

### Main Scripts

1. **pdf_simple_examples.py** - Quick reference examples (START HERE!)
   - Simple table extraction
   - Extract all tables
   - Text + tables together
   - Save to Excel

2. **pdf_text_table_extraction.py** - Comprehensive comparison
   - PyPDF2 for basic text
   - pdfplumber for tables
   - tabula-py for complex tables
   - camelot for high-quality extraction
   - PyMuPDF for speed

3. **medical_pdf_extraction.py** - Medical document processor
   - Extract patient information
   - Lab results parsing
   - Medication lists
   - Vital signs extraction

4. **requirements_pdf.txt** - All dependencies

## 🛠️ Library Comparison

| Library | Best For | Pros | Cons |
|---------|----------|------|------|
| **pdfplumber** ⭐ | General use, tables | Easy, reliable, good quality | Slower on large files |
| **PyPDF2** | Simple text | Fast, lightweight | Poor table support |
| **tabula-py** | Complex tables | Powerful, multi-page | Requires Java |
| **camelot** | Bordered tables | Highest quality | Requires ghostscript |
| **PyMuPDF** | Large files | Very fast | More complex API |

**Recommendation:** Start with **pdfplumber** for most use cases.

## 💡 Common Use Cases

### 1. Extract Single Table

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    tables = pdf.pages[0].extract_tables()
    df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
    df.to_csv("output.csv", index=False)
```

### 2. Extract All Tables from All Pages

```python
import pdfplumber
import pandas as pd

all_tables = []

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
combined = pd.concat(all_tables, ignore_index=True)
combined.to_csv("all_tables.csv", index=False)
```

### 3. Extract Tables with Text

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        # Get text
        text = page.extract_text()
        
        # Get tables
        tables = page.extract_tables()
        
        print(f"Text: {text[:200]}")
        print(f"Tables found: {len(tables)}")
```

### 4. Save to Excel (Multiple Sheets)

```python
import pdfplumber
import pandas as pd

all_tables = []

with pdfplumber.open("document.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        tables = page.extract_tables()
        for table_num, table in enumerate(tables, 1):
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Save to Excel with multiple sheets
with pd.ExcelWriter("output.xlsx") as writer:
    for i, df in enumerate(all_tables, 1):
        df.to_excel(writer, sheet_name=f"Table_{i}", index=False)
```

### 5. Medical Document Processing

```python
from medical_pdf_extraction import MedicalPDFExtractor

with MedicalPDFExtractor("lab_results.pdf") as extractor:
    # Extract structured data
    patient_info = extractor.extract_patient_info()
    lab_results = extractor.extract_lab_results()
    medications = extractor.extract_medication_list()
    
    # Generate comprehensive report
    extractor.generate_report()
```

## 🔧 Advanced Options

### Custom Table Detection

```python
import pdfplumber

table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
}

with pdfplumber.open("document.pdf") as pdf:
    tables = pdf.pages[0].extract_tables(table_settings=table_settings)
```

### Extract Specific Region

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    
    # Define bounding box (x0, top, x1, bottom)
    bbox = (0, 100, 500, 400)
    
    # Extract from specific region
    cropped = page.within_bbox(bbox)
    tables = cropped.extract_tables()
```

### Filter Tables by Content

```python
import pdfplumber

keyword = "Patient"

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if any(keyword in str(row) for row in table):
                # Process matching table
                print("Found matching table!")
```

## 📊 Medical Document Examples

### Lab Results

```python
from medical_pdf_extraction import MedicalPDFExtractor

with MedicalPDFExtractor("lab_results.pdf") as extractor:
    results = extractor.extract_lab_results()
    
    for result in results:
        print(f"{result['test']}: {result['value']} ({result['range']})")
        if result['abnormal']:
            print("  ⚠️ ABNORMAL")
```

### Patient Demographics

```python
with MedicalPDFExtractor("patient_record.pdf") as extractor:
    info = extractor.extract_patient_info()
    print(f"Name: {info.get('name')}")
    print(f"DOB: {info.get('dob')}")
    print(f"MRN: {info.get('mrn')}")
```

### Medication List

```python
with MedicalPDFExtractor("prescriptions.pdf") as extractor:
    meds = extractor.extract_medication_list()
    
    for med in meds:
        print(f"{med['medication']}")
        print(f"  Dose: {med['dose']}")
        print(f"  Frequency: {med['frequency']}")
```

## ⚙️ System Requirements

### Python Packages
```bash
pip install pdfplumber pandas openpyxl --break-system-packages
```

### Optional (for advanced features)

**For tabula-py:**
- Java Runtime Environment (JRE)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install default-jre
  
  # macOS
  brew install java
  ```

**For camelot-py:**
- Ghostscript
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ghostscript
  
  # macOS
  brew install ghostscript
  ```

## 🐛 Troubleshooting

### Issue: No tables detected

**Solutions:**
1. Try different libraries (pdfplumber, tabula, camelot)
2. Adjust table detection settings
3. Check if PDF is scanned image (needs OCR)
4. View PDF structure in Adobe Reader

### Issue: Table structure is wrong

**Solutions:**
1. Use custom table settings
2. Try `flavor='stream'` in camelot for borderless tables
3. Process table post-extraction with pandas

### Issue: Text is garbled

**Solutions:**
1. PDF might be image-based (needs OCR with pytesseract)
2. Try different extraction library
3. Check PDF encoding

### Issue: "Java not found" (tabula-py)

**Solution:**
```bash
# Install Java
sudo apt-get install default-jre

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/default-java
```

### Issue: Import errors

**Solution:**
```bash
# Install all dependencies
pip install pdfplumber pandas openpyxl --break-system-packages

# Or use requirements file
pip install -r requirements_pdf.txt --break-system-packages
```

## 📈 Performance Tips

1. **Use pdfplumber for most cases** - Good balance of speed and accuracy
2. **Use PyMuPDF for large files** - Fastest processing
3. **Process pages in parallel** - Use multiprocessing for big PDFs
4. **Cache results** - Save extracted data to avoid re-processing
5. **Use specific page ranges** - Don't process entire PDF if not needed

## 🔐 Working with Protected PDFs

```python
import pdfplumber

# If PDF is password protected
with pdfplumber.open("protected.pdf", password="your_password") as pdf:
    text = pdf.pages[0].extract_text()
```

## 📝 Best Practices

1. ✅ **Always clean extracted data** - Remove empty rows, strip whitespace
2. ✅ **Validate table structure** - Check headers and column count
3. ✅ **Handle errors gracefully** - PDFs vary widely in structure
4. ✅ **Save intermediate results** - Don't lose work if processing fails
5. ✅ **Test on sample pages first** - Verify extraction quality before batch processing

## 🎯 Next Steps

1. **Start with pdf_simple_examples.py** - Learn the basics
2. **Try on your own PDFs** - Test different extraction methods
3. **Customize for your needs** - Adapt medical_pdf_extraction.py
4. **Batch process** - Add multiprocessing for large datasets
5. **Add validation** - Implement data quality checks

## 📚 Additional Resources

- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [tabula-py Documentation](https://tabula-py.readthedocs.io/)
- [Camelot Documentation](https://camelot-py.readthedocs.io/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

## 🤝 Contributing

Improvements welcome! Common additions:
- OCR support for scanned PDFs
- More medical document templates
- Batch processing utilities
- Data validation functions

## ⚖️ License

These examples are for educational purposes. Ensure you have rights to process PDFs you're working with.

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section
2. Review the error message carefully
3. Try a different extraction library
4. Test with a simple PDF first
5. Verify all dependencies are installed
