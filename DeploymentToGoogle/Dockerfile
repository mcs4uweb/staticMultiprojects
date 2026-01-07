FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Run on port 5001
EXPOSE 5001

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]