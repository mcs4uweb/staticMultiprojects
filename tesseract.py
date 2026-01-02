# AIDEV-NOTE: This script demonstrates various uses of pytesseract for OCR.
# Before running, ensure you have both the pytesseract library and the
# Tesseract OCR engine installed on your system.
# You can install the Python library with: pip install pytesseract Pillow
# For the Tesseract engine itself, follow the installation instructions for your OS.

import pytesseract
from PIL import Image
import requests
import io
import os
from pdf2image import convert_from_path

# =============================================================================
# Configuration
# =============================================================================
# AIDEV-NOTE: Set the path to the tesseract executable if it's not in your PATH.
# This is common on Windows. For example:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# AIDEV-NOTE: Create a dummy image for the examples.
# This simulates having an image file on your system.
try:
    with Image.new('RGB', (400, 200), color='white') as img:
        from PIL import ImageDraw, ImageFont
        d = ImageDraw.Draw(img)
        # You may need to specify a path to a font file if 'arial.ttf' is not found.
        try:
            fnt = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            fnt = ImageFont.load_default()
        d.text((10, 10), "This is an example text.", fill=(0, 0, 0), font=fnt)
        img.save("example_image.png")
    print("Dummy image 'example_image.png' created successfully.")
except Exception as e:
    print(f"Error creating dummy image: {e}")
    exit()

# =============================================================================
# Example 1: Reading text from a local image file
# =============================================================================
def read_text_from_file(image_path):
    """Reads text from a local image file."""
    print(f"\n--- Reading text from {image_path} ---")
    try:
        # AIDEV-NOTE: The core function call is `pytesseract.image_to_string()`.
        # It takes a PIL Image object as input.
        text = pytesseract.image_to_string(Image.open(image_path))
        print(text)
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# =============================================================================
# Example 2: Reading text from a specific region (bounding box)
# =============================================================================
def read_text_from_region(image_path):
    """Reads text from a specific region of an image."""
    print(f"\n--- Reading text from a region of {image_path} ---")
    try:
        img = Image.open(image_path)
        # AIDEV-NOTE: Define the bounding box as a tuple (left, top, right, bottom).
        # This example uses a box that captures the text in our dummy image.
        bounding_box = (0, 0, 400, 100)
        cropped_img = img.crop(bounding_box)
        text = pytesseract.image_to_string(cropped_img)
        print(text)
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# =============================================================================
# Example 3: Reading text from an image URL
# =============================================================================
def read_text_from_url(image_url):
    """Reads text from an image located at a URL."""
    print(f"\n--- Reading text from URL: {image_url} ---")
    try:
        response = requests.get(image_url)
        # AIDEV-NOTE: Use `io.BytesIO` to read the image from the response
        # content in memory without saving it to disk.
        img = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(img)
        print(text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL: {e}")
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# =============================================================================
# Example 4: Reading text from a PDF file
# =============================================================================
def read_text_from_pdf(pdf_path):
    """Reads text from a PDF file."""
    print(f"\n--- Reading text from PDF: {pdf_path} ---")
    try:
        # AIDEV-NOTE: pdf2image converts each page of the PDF into a PIL Image object.
        # This requires the Poppler utility to be installed on your system.
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            print(f"--- Page {i+1} ---")
            text = pytesseract.image_to_string(img)
            print(text)
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# =============================================================================
# Main execution block
# =============================================================================
if __name__ == "__main__":
    # AIDEV-NOTE: Define the paths and URLs for the examples.
    local_image_path = "example_image.png"
    sample_image_url = "https://tesseract-ocr.github.io/tessdoc/images/tesseract.png"
    
    # AIDEV-NOTE: For the PDF example, a sample PDF file named 'sample.pdf'
    # needs to be present in the same directory.
    sample_pdf_path = "sample.pdf"

    read_text_from_file(local_image_path)
    read_text_from_region(local_image_path)
    read_text_from_url(sample_image_url)
    
    # AIDEV-NOTE: Uncomment the following line if you have a sample.pdf to test.
    # read_text_from_pdf(sample_pdf_path)

    # Clean up the dummy image file
    try:
        os.remove(local_image_path)
        print(f"\nCleaned up the dummy image: {local_image_path}")
    except OSError as e:
        print(f"Error during file cleanup: {e}")