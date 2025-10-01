# FastAPI ML Microservice Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for document processing and ChromaDB
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm
RUN python -m spacy download xx_ent_wiki_sm

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/chroma_data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
