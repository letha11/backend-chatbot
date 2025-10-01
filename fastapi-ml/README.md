# FastAPI ML Microservice

The machine learning microservice for the Chatbot Control Panel, handling document processing, embedding generation, and RAG (Retrieval Augmented Generation) chat functionality.

## 🎯 Purpose

This microservice is responsible for:
- **Document Parsing**: Extract text from PDF, DOCX, TXT, and CSV files
- **Text Chunking**: Split documents into manageable segments
- **Embedding Generation**: Convert text to vector embeddings using SentenceTransformers or OpenAI
- **Vector Search**: Find similar document chunks using pgvector
- **RAG Pipeline**: Generate contextual answers using retrieved documents and LLMs

## 🏗️ Architecture

### Services
- **StorageService**: MinIO integration for document retrieval
- **DocumentParser**: Multi-format document parsing
- **EmbeddingService**: Vector embedding generation
- **RAGService**: Complete RAG pipeline with LLM integration

### Models
- **Pydantic Models**: Request/response validation
- **Database Models**: SQLAlchemy models for PostgreSQL

## 🚀 Quick Start

### 📦 Dependencies

This project uses carefully selected dependency versions to avoid conflicts:

- **requirements.txt**: Compatible version ranges for flexibility
- **requirements-lock.txt**: Exact versions for reproducible builds
- **Key fixes**: Resolved `typing-extensions`, `torch`, and other version conflicts

### Development Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (compatible versions)
pip install -r requirements.txt

# Or use locked versions for reproducible builds
pip install -r requirements-lock.txt

# Copy environment file
cp .env.example .env

# Start the service
uvicorn app.main:app --reload --port 8000
```

### Docker Setup
```bash
# Build and run
docker build -t fastapi-ml .
docker run -p 8000:8000 fastapi-ml
```

## 📚 API Endpoints

### Document Processing
#### `POST /parse-document`
Parses an uploaded document and generates embeddings.

**Request:**
```json
{
  "document_id": "uuid",
  "storage_path": "path/to/file",
  "file_type": "pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document parsing started",
  "data": {
    "document_id": "uuid",
    "status": "processing",
    "file_type": "pdf",
    "filename": "document.pdf"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Chat
#### `POST /chat`
Processes a chat query using the RAG pipeline.

**Request:**
```json
{
  "division_id": "uuid",
  "query": "What is the company policy on remote work?"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Chat query processed successfully",
  "data": {
    "query": "What is the company policy on remote work?",
    "answer": "Based on the company handbook...",
    "sources": [
      {
        "filename": "employee-handbook.pdf",
        "chunk_index": 5,
        "distance": 0.15,
        "preview": "Remote work policy states..."
      }
    ],
    "division_id": "uuid",
    "model_used": "gpt-3.5-turbo",
    "total_sources": 3
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Health Check
#### `GET /health`
Returns service health status and configuration.

**Response:**
```json
{
  "status": "success",
  "message": "ML microservice is healthy",
  "data": {
    "service": "FastAPI ML Microservice",
    "version": "1.0.0",
    "environment": "development",
    "database_status": "connected",
    "embedding_service": {
      "provider": "SentenceTransformers",
      "model": "all-MiniLM-L6-v2",
      "dimension": 384
    },
    "rag_service": {
      "llm_model": "gpt-3.5-turbo",
      "max_tokens": 1500,
      "temperature": 0.7,
      "top_k_results": 5,
      "openai_available": true
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 🔧 Configuration

### Environment Variables

#### Database Configuration
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot_control_panel
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chatbot_control_panel
DATABASE_USER=postgres
DATABASE_PASSWORD=password
```

#### MinIO Object Storage
```bash
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=chatbot-documents
MINIO_SECURE=false
```

#### Embedding Configuration
```bash
# Use SentenceTransformers (default)
USE_OPENAI_EMBEDDINGS=false
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Or use OpenAI embeddings
USE_OPENAI_EMBEDDINGS=true
OPENAI_API_KEY=your-openai-api-key
```

#### LLM Configuration
```bash
# Use OpenRouter (recommended for accessing various models)
OPENROUTER_API_KEY=your-openrouter-api-key
USE_OPENROUTER=true
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-oss-120b

# Or use OpenAI directly
OPENAI_API_KEY=your-openai-api-key
USE_OPENROUTER=false
LLM_MODEL=gpt-3.5-turbo

# Common settings
MAX_TOKENS=1500
TEMPERATURE=0.7
```

#### Text Processing
```bash
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

## 🧠 Supported Models

### Embedding Models

#### SentenceTransformers (Local)
- **all-MiniLM-L6-v2** (384 dimensions) - Default, fast and efficient
- **all-mpnet-base-v2** (768 dimensions) - Higher quality
- **multi-qa-mpnet-base-dot-v1** - Optimized for Q&A

#### OpenAI (API)
- **text-embedding-ada-002** (1536 dimensions) - High quality, requires API key

### LLM Models

#### OpenRouter (Recommended)
- **openai/gpt-oss-120b** - Large open-source model with high performance
- **openai/gpt-3.5-turbo** - Fast and cost-effective
- **openai/gpt-4** - Higher quality responses
- **anthropic/claude-3-haiku** - Fast and efficient
- **meta-llama/llama-3.1-405b** - Large open-source model
- **Many more models available** - Check OpenRouter documentation

#### OpenAI Direct
- **gpt-3.5-turbo** - Fast and cost-effective
- **gpt-4** - Higher quality responses
- **gpt-4-turbo** - Latest model with better performance

## 📄 Supported Document Formats

### PDF Files
- **Library**: PyPDF2 + pdfminer.six fallback
- **Features**: Text extraction, table handling, layout preservation
- **Limitations**: Image-based PDFs not supported (OCR not included)

### DOCX Files
- **Library**: python-docx
- **Features**: Paragraph text, table extraction
- **Limitations**: Complex formatting may be lost

### TXT Files
- **Features**: Multiple encoding support (UTF-8, UTF-16, Latin-1)
- **Limitations**: Plain text only

### CSV Files
- **Library**: pandas
- **Features**: Statistical summaries, sample data extraction
- **Output**: Structured text representation of tabular data

## 🔄 Processing Pipeline

### Document Processing Flow
1. **Receive Request**: Express API triggers document parsing
2. **Download File**: Retrieve document from MinIO storage
3. **Parse Content**: Extract text based on file type
4. **Chunk Text**: Split into overlapping segments
5. **Generate Embeddings**: Convert chunks to vectors
6. **Store Embeddings**: Save to PostgreSQL with pgvector
7. **Update Status**: Mark document as "embedded"

### Chat Processing Flow
1. **Receive Query**: User submits question
2. **Generate Query Embedding**: Convert question to vector
3. **Vector Search**: Find similar document chunks using cosine similarity
4. **Construct Context**: Combine retrieved chunks
5. **Generate Response**: Use LLM to create answer
6. **Return Results**: Include answer and source citations
7. **Log Interaction**: Store query/response for analytics

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_parser.py
```

### Test Structure
```
tests/
├── test_parser.py          # Document parsing tests
├── test_embedder.py        # Embedding generation tests
├── test_retriever.py       # RAG pipeline tests
├── test_storage.py         # Storage service tests
└── fixtures/               # Test documents
```

## 🔍 Monitoring and Debugging

### Logging
The service uses structured logging with different levels:
```python
from loguru import logger

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.info("Document processing started")
logger.error("Failed to parse document", error=str(e))
```

### Health Monitoring
- **Database**: Connection health checks
- **Storage**: MinIO connectivity
- **Models**: Embedding service status
- **Memory**: Model loading status

### Performance Metrics
- Document processing time
- Embedding generation speed
- Query response time
- Vector search performance

## 🚨 Error Handling

### Common Error Scenarios

#### Document Processing Errors
- **File Not Found**: Document missing from storage
- **Unsupported Format**: File type not supported
- **Parsing Failed**: Corrupted or invalid document
- **Embedding Failed**: Model or API errors

#### Chat Errors
- **No Results**: No relevant documents found
- **LLM Unavailable**: OpenAI API errors
- **Context Too Large**: Query context exceeds limits

#### System Errors
- **Database Connection**: PostgreSQL connectivity issues
- **Storage Issues**: MinIO access problems
- **Memory Errors**: Model loading failures

## 🔧 Development

### Adding New Document Formats
1. Extend `DocumentParser` class
2. Add parsing method for new format
3. Update file type validation
4. Add tests for new format

### Custom Embedding Models
1. Implement embedding interface
2. Add model configuration
3. Update dimension settings
4. Test compatibility with pgvector

### Custom LLM Integration
1. Extend `RAGService` class
2. Implement LLM client interface
3. Add model configuration
4. Update prompt templates

## 📊 Performance Optimization

### Embedding Generation
- **Batch Processing**: Process multiple chunks together
- **Model Caching**: Keep models in memory
- **GPU Support**: Use CUDA for faster inference

### Vector Search
- **Index Optimization**: Configure pgvector indexes
- **Query Optimization**: Efficient similarity searches
- **Result Caching**: Cache frequent queries

### Memory Management
- **Model Loading**: Load models on startup
- **Cleanup**: Proper resource cleanup
- **Monitoring**: Track memory usage

## 🤝 Contributing

1. Follow Python PEP 8 style guide
2. Add type hints to all functions
3. Write comprehensive tests
4. Update documentation
5. Use conventional commit messages

---

**Part of the Chatbot Control Panel Backend System**
