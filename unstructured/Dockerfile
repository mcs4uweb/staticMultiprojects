FROM python:3.11-slim

# Install Tesseract for OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingest.py app.py ./

# Expose API port
EXPOSE 8000

# Default command: start the query API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]