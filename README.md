# Chatbot Control Panel Backend

A comprehensive document management and RAG (Retrieval Augmented Generation) chatbot system built with Express.js and FastAPI microservices architecture, featuring **OpenRouter integration** for accessing various LLM models including `openai/gpt-oss-120b`.

## 🏗️ Architecture Overview

This project uses a microservices architecture with two main components:

### **Express.js API** (`express-api/`)
- **Purpose**: Main backend API for CRUD operations, authentication, and user management
- **Technology**: TypeScript, Express.js, TypeORM, PostgreSQL
- **Port**: 3000
- **Responsibilities**:
  - User authentication and authorization (JWT)
  - Division management
  - Document upload and metadata management
  - API gateway for ML services
  - Standardized response handling

### **FastAPI ML Microservice** (`fastapi-ml/`)
- **Purpose**: Document processing, embedding generation, and RAG chat pipeline
- **Technology**: Python, FastAPI, SentenceTransformers/OpenRouter, pgvector
- **Port**: 8000
- **Responsibilities**:
  - Document parsing (PDF, DOCX, TXT, CSV)
  - Text chunking and embedding generation
  - Vector similarity search
  - RAG-based chat responses with OpenRouter LLMs
  - ML model management

## 🌟 OpenRouter Integration

This system is configured to use **OpenRouter** for accessing various LLM models, including the powerful `openai/gpt-oss-120b` model. OpenRouter provides:

- **Access to Multiple Models**: GPT, Claude, Llama, and many open-source models
- **Cost Optimization**: Compare prices across different providers
- **OpenAI API Compatible**: Drop-in replacement for OpenAI API calls
- **No Vendor Lock-in**: Easy switching between models

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Option 1: Production (Docker)
```bash
# 1. Set your OpenRouter API key in docker-compose.yml
# Edit docker-compose.yml and uncomment:
# OPENROUTER_API_KEY: your_openrouter_api_key_here

# 2. Start all services
./scripts/start-prod.sh

# Or manually:
docker compose up --build -d
```

### Option 2: Development
```bash
# 1. Start infrastructure services
./scripts/start-dev.sh

# 2. Configure FastAPI ML service
cd fastapi-ml
cp .env.example .env
# Edit .env and add your OpenRouter API key:
# OPENROUTER_API_KEY=your_openrouter_api_key_here

# 3. In a new terminal, start Express API
cd express-api
cp env.example .env
npm install
npm run migration:run
npm run dev
```

## 🔑 OpenRouter Setup

### 1. Get API Key
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Create an account and add credits
3. Generate an API key

### 2. Configure Environment
```bash
# FastAPI ML service (.env)
OPENROUTER_API_KEY=your_openrouter_api_key_here
USE_OPENROUTER=true
LLM_MODEL=openai/gpt-oss-120b
```

### 3. Available Models
```bash
# Large open-source models
LLM_MODEL=openai/gpt-oss-120b          # Your requested model
LLM_MODEL=meta-llama/llama-3.1-405b    # Meta's largest model
LLM_MODEL=meta-llama/llama-3.1-70b     # Efficient large model

# OpenAI models via OpenRouter
LLM_MODEL=openai/gpt-4-turbo
LLM_MODEL=openai/gpt-3.5-turbo

# Anthropic models
LLM_MODEL=anthropic/claude-3-opus
LLM_MODEL=anthropic/claude-3-haiku
```

## 🌐 Service URLs

- **Express API**: http://localhost:3000
- **FastAPI ML**: http://localhost:8000
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **PostgreSQL**: localhost:5432

## 📚 API Documentation

### Express.js API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new admin user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

#### Division Management
- `GET /api/v1/divisions` - List all divisions
- `POST /api/v1/divisions` - Create division
- `GET /api/v1/divisions/:id` - Get division by ID
- `PUT /api/v1/divisions/:id` - Update division
- `DELETE /api/v1/divisions/:id` - Delete division

#### Document Management
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/:id` - Get document by ID
- `PATCH /api/v1/documents/:id/toggle` - Toggle document active status
- `DELETE /api/v1/documents/:id` - Delete document

#### Chat (RAG with OpenRouter)
- `POST /api/v1/chat` - Process chat query using RAG with OpenRouter LLMs

#### Conversations
- `GET /api/v1/conversations?division_id=<uuid>&limit=50` - List current user's conversations (JWT required)
- `POST /api/v1/conversations/ingest` - Internal endpoint to create/append conversation messages (requires `x-internal-api-key`)
- `GET /api/v1/conversations/:conversation_id/history?limit=6` - Internal: Get last N messages for RAG context (requires `x-internal-api-key`)

### FastAPI ML Endpoints

#### Document Processing
- `POST /parse-document` - Parse and embed document
- `GET /health` - Health check

#### Chat
- `POST /chat` - RAG chat pipeline with OpenRouter integration

## 🔄 Document Processing Pipeline

1. **Upload**: Document uploaded via Express API to MinIO storage
2. **Parse**: FastAPI ML service retrieves and parses document content
3. **Chunk**: Text is split into manageable chunks with overlap
4. **Embed**: Chunks are converted to vector embeddings
5. **Store**: Embeddings stored in PostgreSQL with pgvector
6. **Activate**: Document becomes available for chat queries

## 💬 RAG Chat Pipeline with OpenRouter

1. **Query**: User submits question through Express API
2. **Embed**: Query converted to vector embedding
3. **Search**: Vector similarity search finds relevant chunks
4. **Context**: Retrieved chunks combined into context
5. **Generate**: **OpenRouter LLM** (e.g., `openai/gpt-oss-120b`) generates answer
6. **Response**: Answer returned with source citations

## 🔧 Configuration

### Express API Environment Variables
```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chatbot_control_panel
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# JWT
JWT_SECRET=your-secret-key

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents

# FastAPI ML Service
FASTAPI_URL=http://localhost:8000

# Internal integration (FastAPI → Express)
INTERNAL_API_KEY=your-internal-key
```

### FastAPI ML Environment Variables
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot_control_panel

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# OpenRouter Configuration (Recommended)
OPENROUTER_API_KEY=your-openrouter-api-key
USE_OPENROUTER=true
LLM_MODEL=openai/gpt-oss-120b

# Or OpenAI Direct
OPENAI_API_KEY=your-openai-api-key
USE_OPENROUTER=false
LLM_MODEL=gpt-3.5-turbo

# Embedding Model (Local)
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Express API integration
EXPRESS_API_URL=http://localhost:3000
INTERNAL_API_KEY=your-internal-key
CONVERSATION_HISTORY_LIMIT=6
```

## 🧪 Testing the Integration

### 1. Check Health
```bash
curl http://localhost:8000/health
```

Look for OpenRouter status in the response:
```json
{
  "data": {
    "rag_service": {
      "llm_model": "openai/gpt-oss-120b",
      "llm_provider": "OpenRouter",
      "llm_available": true,
      "openrouter_enabled": true
    }
  }
}
```

### 2. Test Chat
```bash
# Login first
TOKEN=$(curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}' | jq -r '.data.token')

# Upload a document
DIVISION_ID=$(curl -X POST http://localhost:3000/api/v1/divisions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Division"}' | jq -r '.data.id')

# Upload document
curl -X POST http://localhost:3000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your_document.pdf" \
  -F "division_id=$DIVISION_ID"

# Wait for processing, then chat
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"division_id\": \"$DIVISION_ID\", \"query\": \"What is this document about?\"}"
```

### 2b. Continue Chat in an Existing Conversation
```bash
# Use conversation_id returned from previous call
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"division_id\": \"$DIVISION_ID\", \"query\": \"Follow-up question...\", \"conversation_id\": \"<conversation_id>\"}"
```

## 📊 Database Schema

### Core Tables
- **users**: Admin user accounts with JWT authentication
- **divisions**: Document categories/divisions
- **documents**: Document metadata and status tracking
- **embeddings**: Vector embeddings with pgvector support
- **user_queries**: Chat interaction logging

## 🔧 Monitoring and Logs

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker logs -f chatbot-express-api
docker logs -f chatbot-fastapi-ml
```

### 3. Test Conversations Ingestion (from FastAPI or internal use)
```bash
# Create a new conversation with two messages
curl -X POST http://localhost:3000/api/v1/conversations/ingest \
  -H "x-internal-api-key: $INTERNAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Main theme/topic generated in first turn",
    "division_id": "'$DIVISION_ID'",
    "messages": [
      { "role": "user", "content": "User first question..." },
      { "role": "assistant", "content": "Assistant answer..." }
    ]
  }'

# Fetch the last 6 messages for RAG context
curl "http://localhost:3000/api/v1/conversations/<conversation_id>/history?limit=6" \
  -H "x-internal-api-key: $INTERNAL_API_KEY"
```

### 4. List Current User's Conversations
```bash
curl -X GET "http://localhost:3000/api/v1/conversations?division_id=$DIVISION_ID&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### Health Checks
- Express API: `GET http://localhost:3000/health`
- FastAPI ML: `GET http://localhost:8000/health`

## 📦 Project Structure

```
backend/
├── express-api/          # Express.js API service
│   ├── src/
│   │   ├── controllers/  # API route handlers (includes chatController)
│   │   ├── routes/       # API route definitions (includes chatRoutes)
│   │   └── ...
│   └── Dockerfile
├── fastapi-ml/           # FastAPI ML microservice
│   ├── app/
│   │   ├── services/     # ML services (parsing, embedding, RAG)
│   │   ├── config.py     # OpenRouter configuration
│   │   └── main.py       # FastAPI application
│   └── Dockerfile
├── scripts/              # Startup scripts
├── docker-compose.yml    # Production setup with OpenRouter
├── docker-compose.dev.yml # Development setup
├── OPENROUTER_SETUP.md   # Detailed OpenRouter setup guide
└── README.md            # This file
```

## 📚 Documentation

- **[OpenRouter Setup Guide](OPENROUTER_SETUP.md)** - Detailed OpenRouter configuration
- **[Express API README](express-api/README.md)** - Express.js service documentation
- **[FastAPI ML README](fastapi-ml/README.md)** - FastAPI ML service documentation
- **[API Response Structure](express-api/docs/API_RESPONSE_STRUCTURE.md)** - Standardized API responses

## 💰 Cost Considerations

OpenRouter provides transparent pricing across different models:

- **openai/gpt-oss-120b**: Cost-effective large open-source model
- **Pricing varies**: Check [OpenRouter pricing](https://openrouter.ai/models?pricing=true)
- **Monitor usage**: Use OpenRouter dashboard to track costs
- **Optimize context**: Adjust `TOP_K_RESULTS` to control context size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **OpenRouter Issues**: Check [OpenRouter documentation](https://openrouter.ai/docs)
- **General Issues**: Create an issue in the repository
- **Setup Help**: See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md)

---

**Built with ❤️ using Express.js, FastAPI, OpenRouter, PostgreSQL, and Docker**

**Ready to chat with your documents using OpenRouter's powerful LLMs!** 🚀
