import base64
import binascii
import os
from typing import Union


def _clean_base64_string(b64: Union[str, bytes]) -> bytes:
    """Remove data URL prefix and return bytes suitable for b64decode."""
    if isinstance(b64, bytes):
        s = b64
    else:
        s = b64.strip()
        # remove data URL prefix if present
        if ',' in s and s.lower().startswith('data:'):
            s = s.split(',', 1)[1]
        s = s.encode('ascii')
    return s


def base64_to_pdf(base64_string: Union[str, bytes], output_filename: str) -> bool:
    """
    Convert a base64 string to a PDF file.

    Returns True on success, False on error.
    """
    try:
        b = _clean_base64_string(base64_string)
        # validate=True rejects non-base64 bytes
        pdf_data = base64.b64decode(b, validate=True)

        os.makedirs(os.path.dirname(output_filename) or '.', exist_ok=True)
        with open(output_filename, 'wb') as pdf_file:
            pdf_file.write(pdf_data)

        print(f"PDF successfully saved as '{output_filename}' ({len(pdf_data)} bytes)")
        return True

    except (binascii.Error, ValueError):
        print("Error: invalid base64 data")
        return False
    except FileNotFoundError:
        print("Error: invalid file path")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def quick_base64_to_pdf(b64_string: Union[str, bytes], filename: str) -> None:
    """Quick one-liner conversion (raises on error)."""
    b = _clean_base64_string(b64_string)
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(b, validate=True))


def safe_base64_to_pdf(base64_string: Union[str, bytes], output_path: str) -> bool:
    """Same as base64_to_pdf but explicit name for clarity."""
    return base64_to_pdf(base64_string, output_path)


# Example usage (remove or replace the sample string)
if __name__ == "__main__":
    # Put your base64 (or data URL) string here. Keep it small or load from file.
    sample_b64 = "JVBERi0xLjQK..."  # truncated example
    base64_to_pdf(sample_b64, "output_document.pdf")
