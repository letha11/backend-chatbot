# Chatbot Control Panel Backend

A robust backend system for managing chatbot document storage, processing, and retrieval using Express.js, TypeScript, PostgreSQL with pgvector, and MinIO for object storage.

## Features

### Phase 2: Database & Storage Setup ✅
- PostgreSQL with pgvector extension for vector similarity search
- Comprehensive database schema with proper relationships
- MinIO integration for local object storage
- Database migrations using TypeORM

### Phase 3: Backend Foundations ✅
- Express.js with TypeScript
- JWT-based authentication system
- Division management (CRUD operations)
- Document management with file upload
- Integration with FastAPI microservice for document processing
- RAG chat endpoint with OpenRouter/OpenAI LLM integration
- Comprehensive error handling and logging

## Prerequisites

- Node.js (v18 or higher)
- PostgreSQL (v14 or higher) with pgvector extension
- MinIO server (for local object storage)
- FastAPI microservice (for document processing)

## Installation

1. **Clone and setup the project:**
   ```bash
   cd backend
   npm install
   ```

2. **Setup environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Setup PostgreSQL with pgvector:**
   ```bash
   # Install PostgreSQL and pgvector extension
   # On macOS with Homebrew:
   brew install postgresql pgvector
   
   # Start PostgreSQL
   brew services start postgresql
   
   # Create database
   createdb chatbot_control_panel
   ```

4. **Setup MinIO (Local Object Storage):**
   ```bash
   # Using Docker:
   docker run -p 9000:9000 -p 9001:9001 \
     --name minio \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     -v /tmp/data:/data \
     quay.io/minio/minio server /data --console-address ":9001"
   ```

5. **Run database migrations:**
   ```bash
   npm run migration:run
   ```

6. **Start the development server:**
   ```bash
   npm run dev
   ```

## API Response Structure

All API endpoints return responses in a standardized format:

```json
{
  "status": "success" | "error",
  "message": "Human readable message",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { "result": "data" },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

See `docs/API_RESPONSE_STRUCTURE.md` for complete documentation.

## API Documentation

### Authentication

#### Register Admin User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "admin",
  "password": "securepassword",
  "role": "admin"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "securepassword"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <jwt_token>
```

### Division Management

#### Create Division
```http
POST /api/v1/divisions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Engineering",
  "description": "Engineering team documents",
  "is_active": true
}
```

#### Get All Divisions
```http
GET /api/v1/divisions
Authorization: Bearer <jwt_token>
```

#### Get Division by ID
```http
GET /api/v1/divisions/{division_id}
Authorization: Bearer <jwt_token>
```

#### Update Division
```http
PUT /api/v1/divisions/{division_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Updated Engineering",
  "description": "Updated description"
}
```

#### Delete Division (Soft Delete)
```http
DELETE /api/v1/divisions/{division_id}
Authorization: Bearer <jwt_token>
```

### Document Management

#### Upload Document
```http
POST /api/v1/documents/upload
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <document_file>
division_id: <division_uuid>
```

#### Get All Documents
```http
GET /api/v1/documents
Authorization: Bearer <jwt_token>

# Optional query parameters:
# ?division_id=<uuid>
# ?is_active=true|false
```

#### Get Document by ID
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <jwt_token>
```

#### Toggle Document Active Status
```http
PATCH /api/v1/documents/{document_id}/toggle
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "is_active": true
}
```

#### Delete Document
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <jwt_token>
```

## Database Schema

### Tables
- `users` - Admin user accounts
- `divisions` - Document categories/divisions
- `documents` - Document metadata and status
- `embeddings` - Vector embeddings for document chunks
- `user_queries` - Query history and analytics

### Key Features
- UUID primary keys for all entities
- Proper foreign key relationships
- Vector similarity search using pgvector
- Soft deletes for divisions and documents
- Comprehensive indexing for performance

## File Storage

The system uses MinIO for local object storage, which provides S3-compatible APIs. Documents are stored with UUID-based filenames to prevent conflicts.

## Error Handling

- Comprehensive error handling middleware
- Structured error responses
- Request/response logging
- Graceful shutdown handling

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation using Joi
- CORS and Helmet security middleware
- File type restrictions for uploads

## Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server
- `npm test` - Run all tests
- `npm run test:unit` - Run unit tests only
- `npm run test:integration` - Run integration tests only
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate test coverage report
- `npm run migration:generate` - Generate new migration
- `npm run migration:run` - Run pending migrations
- `npm run migration:revert` - Revert last migration

## Environment Variables

See `env.example` for all available configuration options.

## Integration with FastAPI Microservice

The backend integrates with a FastAPI Python microservice for document processing:
- Triggers document parsing after upload
- Handles embedding generation
- Manages document processing status updates

The FastAPI service should be running on the URL specified in `FASTAPI_URL` environment variable.

## Testing

The project includes comprehensive test coverage with both unit and integration tests.

### Test Coverage
- **Authentication**: Registration, login, token validation, edge cases
- **Division Management**: CRUD operations, validation, authorization
- **Document Management**: File upload, status management, filtering
- **Integration Workflows**: End-to-end user journeys
- **Edge Cases**: Input validation, error handling, service failures

### Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage

# Run comprehensive test suite (includes setup)
./tests/runTests.sh
```

### Test Database Setup
Tests use a separate PostgreSQL database (`chatbot_control_panel_test`) with automatic:
- Schema synchronization
- Data cleanup between tests
- pgvector extension setup

See `tests/README.md` for detailed testing documentation.

## Postman Collection

A comprehensive Postman collection is available for API testing and development:

### Quick Import
1. Open Postman
2. Import both files from the `postman/` directory:
   - `Chatbot-Control-Panel-Backend.postman_collection.json`
   - `Chatbot-Control-Panel-Environment.postman_environment.json`
3. Select the "Chatbot Control Panel Environment"
4. Start testing!

### Features
- ✅ **All 15 API endpoints** with sample requests
- ✅ **Automatic authentication** token management
- ✅ **Test scripts** with response validation
- ✅ **Environment variables** auto-managed
- ✅ **Error scenarios** and edge case testing
- ✅ **Complete workflows** for end-to-end testing
- ✅ **File upload testing** with proper form data

### Quick Test Sequence
1. **Health Check** → Verify server is running
2. **Register & Login** → Get authentication token
3. **Create Division** → Set up document organization
4. **Upload Document** → Test file processing
5. **Manage Documents** → Test full document lifecycle

See `postman/README.md` for complete documentation and `postman/QUICK_START.md` for immediate setup.
