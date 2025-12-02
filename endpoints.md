# API Endpoints Documentation

This document provides a comprehensive overview of all available API endpoints in the Chatbot Control Panel system. The system consists of two main services:

1. **Express.js Backend API** (Port 3000) - Main CRUD operations, authentication, and business logic
2. **FastAPI ML Service** (Port 8000) - Document processing, embeddings, and RAG chat functionality

## Response Format

All endpoints return standardized JSON responses:

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { /* response data */ },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error description",
  "errors": ["detailed", "error", "messages"],  // optional
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

# Express.js Backend API (Port 3000)

Base URL: `http://localhost:3000`

## Health Check

### GET /health
Check the health status of the backend service.

**Authentication:** None required  
**Response:** Service health information including version and environment

**Example Response:**
```json
{
  "status": "success",
  "message": "Service is healthy",
  "data": {
    "service": "Chatbot Control Panel Backend",
    "version": "1.0.0",
    "environment": "development"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## Authentication Endpoints

Base path: `/api/v1/auth`

### POST /api/v1/auth/register
Register a new admin user.

**Status:** DISABLED (commented out in routes)  
**Authentication:** None required  
**Request Body:**
```json
{
  "username": "string (3-30 chars, alphanumeric)",
  "password": "string (min 5 chars)",
  "role": "admin | super_admin | user" // optional, defaults to "user"
}
```

**Note:** This endpoint is currently disabled in the implementation. User registration should be done through the user management endpoints by super_admin users.

### POST /api/v1/auth/login
Authenticate user and receive JWT token.

**Authentication:** None required  
**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Example Request:**
```json
{
  "username": "admin",
  "password": "admin123456"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDEwODE2MDB9.abc123def456ghi789",
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Admin User",
      "username": "admin",
      "role": "admin"
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Invalid credentials",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/auth/me
Get current authenticated user information.

**Authentication:** Bearer token required  
**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "User profile retrieved successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Admin User",
    "username": "admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Access token required",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## Division Management

Base path: `/api/v1/divisions`  
**Authentication:** All endpoints require Bearer token

### POST /api/v1/divisions
Create a new division.

**Request Body:**
```json
{
  "name": "string (1-255 chars, required, unique)",
  "description": "string (optional)",
  "is_active": "boolean (optional, defaults to true)"
}
```

**Example Request:**
```json
{
  "name": "Engineering",
  "description": "Engineering team documents and resources",
  "is_active": true
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Division created successfully",
  "data": {
    "id": "456e7890-e12b-34c5-d678-901234567890",
    "name": "Engineering",
    "description": "Engineering team documents and resources",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Division name already exists",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/divisions
Get all divisions.

**Query Parameters:**
- `is_active`: boolean (optional) - Filter by active status

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Divisions retrieved successfully",
  "data": [
    {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Engineering",
      "description": "Engineering team documents and resources",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    },
    {
      "id": "789e0123-e45f-67g8-h901-234567890123",
      "name": "Marketing",
      "description": "Marketing team documents",
      "is_active": true,
      "created_at": "2024-01-01T11:00:00.000Z",
      "updated_at": "2024-01-01T11:00:00.000Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/divisions/:id
Get a specific division by UUID.

**Path Parameters:**
- `id`: UUID of the division

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Division retrieved successfully",
  "data": {
    "id": "456e7890-e12b-34c5-d678-901234567890",
    "name": "Engineering",
    "description": "Engineering team documents and resources",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Division not found",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/divisions/default
Get the default division (only available when division feature is disabled).

**Note:** This endpoint is only available when `config.features.division` is `false`. When division feature is enabled, use `/api/v1/divisions/:id` instead.

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Default division retrieved successfully",
  "data": {
    "id": "456e7890-e12b-34c5-d678-901234567890",
    "name": "Default",
    "description": "Default division",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### PUT /api/v1/divisions/:id
Update an existing division.

**Path Parameters:**
- `id`: UUID of the division

**Request Body:** (all fields optional, at least one required)
```json
{
  "name": "string (1-255 chars)",
  "description": "string",
  "is_active": "boolean"
}
```

**Example Request:**
```json
{
  "name": "Updated Engineering Division",
  "description": "Updated description for engineering team",
  "is_active": true
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Division updated successfully",
  "data": {
    "id": "456e7890-e12b-34c5-d678-901234567890",
    "name": "Updated Engineering Division",
    "description": "Updated description for engineering team",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:05:00.000Z"
  },
  "timestamp": "2024-01-01T12:05:00.000Z"
}
```

### DELETE /api/v1/divisions/:id
Soft delete a division (sets is_active to false).

**Path Parameters:**
- `id`: UUID of the division

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Division deactivated successfully",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** The response does not include a `data` field for delete operations.

---

## Document Management

Base path: `/api/v1/documents`  
**Authentication:** All endpoints require Bearer token

### POST /api/v1/documents/upload
Upload a new document file.

**Content-Type:** `multipart/form-data`  
**File Size Limit:** 50MB  
**Allowed File Types:** PDF, DOCX, DOC, TXT, CSV, JPEG, PNG, JPG

**Form Data:**
- `file`: File to upload (required)
- `division_id`: UUID of the target division (required when division feature is enabled, ignored when disabled)

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Document uploaded successfully",
  "data": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "division_id": "456e7890-e12b-34c5-d678-901234567890",
    "original_filename": "technical_manual.pdf",
    "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
    "file_type": "pdf",
    "status": "uploaded",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** 
- The document is created with `is_active: true` initially
- Document parsing is triggered asynchronously via FastAPI microservice
- SSE events are sent to notify frontend about parsing status

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Invalid file type. Only PDF, DOCX, DOC, TXT, CSV, and image files are allowed.",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/documents
Get all documents with optional filtering.

**Query Parameters:**
- `division_id`: UUID (optional) - Filter by division (only used when division feature is enabled)
- `is_active`: boolean (optional) - Filter by active status

**Note:** When division feature is disabled (`config.features.division = false`), documents are automatically filtered by the default division.

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Documents retrieved successfully",
  "data": [
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "division_id": "456e7890-e12b-34c5-d678-901234567890",
      "original_filename": "technical_manual.pdf",
      "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
      "file_type": "pdf",
      "status": "embedded",
      "is_active": true,
      "uploaded_by": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:05:00.000Z",
      "division": {
        "id": "456e7890-e12b-34c5-d678-901234567890",
        "name": "Engineering"
      }
    },
    {
      "id": "xyz98765-abc4-3210-defg-hijklmnopqrs",
      "division_id": "789e0123-e45f-67g8-h901-234567890123",
      "original_filename": "marketing_guidelines.docx",
      "storage_path": "xyz98765-abc4-3210-defg-hijklmnopqrs.docx",
      "file_type": "docx",
      "status": "parsing_failed",
      "is_active": false,
      "uploaded_by": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2024-01-01T11:30:00.000Z",
      "updated_at": "2024-01-01T11:35:00.000Z",
      "division": {
        "id": "789e0123-e45f-67g8-h901-234567890123",
        "name": "Marketing"
      }
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/documents/:id
Get a specific document by UUID.

**Path Parameters:**
- `id`: UUID of the document

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Document retrieved successfully",
  "data": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "division_id": "456e7890-e12b-34c5-d678-901234567890",
    "original_filename": "technical_manual.pdf",
    "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
    "file_type": "pdf",
    "status": "embedded",
    "is_active": true,
    "uploaded_by": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:05:00.000Z",
    "division": {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Engineering",
      "description": "Engineering team documents and resources"
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### PATCH /api/v1/documents/:id/toggle
Toggle the active status of a document.

**Path Parameters:**
- `id`: UUID of the document

**Request Body:**
```json
{
  "is_active": "boolean (required)"
}
```

**Example Request:**
```json
{
  "is_active": true
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Document activated successfully",
  "data": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "division_id": "456e7890-e12b-34c5-d678-901234567890",
    "original_filename": "technical_manual.pdf",
    "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
    "file_type": "pdf",
    "status": "embedded",
    "is_active": true,
    "uploaded_by": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:05:00.000Z"
  },
  "timestamp": "2024-01-01T12:05:00.000Z"
}
```

**Note:** If vector database sync fails, the message will include a warning: "(Note: Vector database sync failed, but document status updated in main database)"

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Document must be embedded before it can be activated",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** Documents can only be activated if their status is 'embedded'

### DELETE /api/v1/documents/:id
Delete a document (removes from storage and database).

**Path Parameters:**
- `id`: UUID of the document

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** 
- The response does not include a `data` field for delete operations
- If vector database cleanup fails, the message will include a warning: "(Note: Vector database cleanup failed, but document deleted from main database)"
- The document is also deleted from ChromaDB and OpenSearch via FastAPI microservice

---

## Chat Endpoint

Base path: `/api/v1/chat`  
**Authentication:** Bearer token required

### POST /api/v1/chat
Process a chat query using RAG pipeline (proxies to FastAPI ML service).

**Request Body:**
```json
{
  "division_id": "UUID (required when division feature is enabled)",
  "query": "string (1-2000 chars, required)",
  "conversation_id": "UUID (optional)",
  "title": "string (optional)"
}
```

**Note:** When division feature is disabled (`config.features.division = false`), `division_id` is automatically set to the default division.

**Example Request:**
```json
{
  "division_id": "456e7890-e12b-34c5-d678-901234567890",
  "query": "What are the safety protocols for handling electrical equipment?",
  "conversation_id": "789e0123-e45f-67g8-h901-234567890123",
  "title": "Safety Protocols Discussion"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Chat query processed successfully",
  "data": {
    "query": "What are the safety protocols for handling electrical equipment?",
    "answer": "Based on the technical manual, the safety protocols for handling electrical equipment include: 1) Always turn off power at the main breaker before working on electrical systems, 2) Use appropriate PPE including insulated gloves and safety glasses, 3) Test circuits with a multimeter before touching any wires, 4) Never work alone on high-voltage systems, and 5) Follow lockout/tagout procedures to prevent accidental energization.",
    "sources": [
      {
        "filename": "technical_manual.pdf",
        "chunk_index": 12,
        "distance": 0.23,
        "preview": "Safety protocols for electrical work must be strictly followed. Always turn off power at the main breaker before beginning any electrical work. Use appropriate personal protective equipment..."
      },
      {
        "filename": "technical_manual.pdf", 
        "chunk_index": 13,
        "distance": 0.31,
        "preview": "Testing circuits is essential before any maintenance. Use a multimeter to verify that circuits are de-energized. Never assume a circuit is safe without proper testing..."
      }
    ],
    "division": {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Engineering"
    },
    "model_used": "openai/gpt-oss-120b",
    "total_sources": 2,
    "conversation_id": "789e0123-e45f-67g8-h901-234567890123"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "No relevant documents found for this query",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## Conversation Management

Base path: `/api/v1/conversations`  
**Authentication:** Bearer token required (except internal endpoints)

### POST /api/v1/conversations/ingest
Ingest conversation messages (internal API only).

**Authentication:** Internal API key required (`x-internal-api-key` header)  
**Request Body:**
```json
{
  "conversation_id": "UUID (optional)",
  "division_id": "UUID (optional)",
  "title": "string (required when creating new conversation)",
  "user_id": "UUID (optional)",
  "messages": [
    {
      "role": "user | assistant | system",
      "content": "string",
      "sources": "string (optional)"
    }
  ]
}
```

**Note:** When division feature is disabled (`config.features.division = false`), `division_id` is automatically set to the default division.

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Conversation messages ingested",
  "data": {
    "conversation_id": "789e0123-e45f-67g8-h901-234567890123",
    "title": "Safety Protocols Discussion",
    "inserted_messages": 2
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/conversations/:conversation_id/history
Get conversation history for a specific conversation (public API with JWT authentication).

**Authentication:** Bearer token required  
**Path Parameters:**
- `conversation_id`: UUID of the conversation

**Query Parameters:**
- `limit`: integer (optional, max 20, default 6)

**Example Success Response:**
```json
{
  "status": "success",
  "data": {
    "conversation": {
      "id": "789e0123-e45f-67g8-h901-234567890123",
      "title": "Safety Protocols Discussion",
      "division_id": "456e7890-e12b-34c5-d678-901234567890",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2024-01-01T10:00:00.000Z"
    },
    "messages": [
      {
        "id": "msg-001",
        "role": "user",
        "content": "What are the safety protocols?",
        "sources": null,
        "created_at": "2024-01-01T10:05:00.000Z"
      },
      {
        "id": "msg-002",
        "role": "assistant",
        "content": "Based on the technical manual...",
        "sources": "[{\"filename\":\"manual.pdf\",\"chunk_index\":5}]",
        "created_at": "2024-01-01T10:05:30.000Z"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "You are not allowed to access this conversation",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** Users can only access conversations that belong to them (`user_id` must match the authenticated user).

### GET /api/v1/conversations/:conversation_id/history-internal
Get conversation history for a specific conversation (internal API only).

**Authentication:** Internal API key required (`x-internal-api-key` header)  
**Path Parameters:**
- `conversation_id`: UUID of the conversation

**Query Parameters:**
- `limit`: integer (optional, max 20, default 6)

**Example Success Response:**
```json
{
  "status": "success",
  "data": {
    "conversation": {
      "id": "789e0123-e45f-67g8-h901-234567890123",
      "title": "Safety Protocols Discussion",
      "division_id": "456e7890-e12b-34c5-d678-901234567890",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2024-01-01T10:00:00.000Z"
    },
    "messages": [
      {
        "id": "msg-001",
        "role": "user",
        "content": "What are the safety protocols?",
        "sources": null,
        "created_at": "2024-01-01T10:05:00.000Z"
      },
      {
        "id": "msg-002",
        "role": "assistant",
        "content": "Based on the technical manual...",
        "sources": "[{\"filename\":\"manual.pdf\",\"chunk_index\":5}]",
        "created_at": "2024-01-01T10:05:30.000Z"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** This endpoint does not check user ownership and is intended for internal use by the FastAPI ML service.

### GET /api/v1/conversations
List conversations for the current user.

**Authentication:** Bearer token required  
**Query Parameters:**
- `division_id`: UUID (optional) - Filter by division (only used when division feature is enabled)
- `limit`: integer (optional, max 200, default 50)

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Conversations retrieved successfully",
  "data": {
    "conversations": [
      {
        "id": "789e0123-e45f-67g8-h901-234567890123",
        "title": "Safety Protocols Discussion",
        "division_id": "456e7890-e12b-34c5-d678-901234567890",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T10:00:00.000Z",
        "updated_at": "2024-01-01T10:05:30.000Z"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** 
- Conversations are ordered by `updated_at` in descending order (most recent first)
- When division feature is disabled, conversations are automatically filtered by the default division

---

## User Management

Base path: `/api/v1/users`  
**Authentication:** Bearer token + super_admin role required

### GET /api/v1/users
List all users.

**Example Success Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Admin User",
      "username": "admin",
      "role": "admin",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00.000Z",
      "updated_at": "2024-01-01T10:00:00.000Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/v1/users/:id
Get a specific user by UUID.

**Path Parameters:**
- `id`: UUID of the user

**Example Success Response:**
```json
{
  "status": "success",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Admin User",
    "username": "admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000Z",
    "updated_at": "2024-01-01T10:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### POST /api/v1/users
Create a new user.

**Request Body:**
```json
{
  "name": "string (optional)",
  "username": "string (3-30 chars, alphanumeric, required)",
  "password": "string (min 5 chars, required)",
  "role": "admin | super_admin | user (optional, defaults to 'user')",
  "is_active": "boolean (optional, defaults to true)"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "User created",
  "data": {
    "user": {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "New User",
      "username": "newuser",
      "role": "user",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### PUT /api/v1/users/:id
Update an existing user.

**Path Parameters:**
- `id`: UUID of the user

**Request Body:** (all fields optional, at least one required)
```json
{
  "name": "string (optional)",
  "username": "string (3-30 chars, alphanumeric)",
  "password": "string (min 5 chars)",
  "role": "admin | super_admin | user",
  "is_active": "boolean"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "User updated",
  "data": {
    "user": {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Updated User",
      "username": "updateduser",
      "role": "admin",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:05:00.000Z"
    }
  },
  "timestamp": "2024-01-01T12:05:00.000Z"
}
```

### DELETE /api/v1/users/:id
Delete a user.

**Path Parameters:**
- `id`: UUID of the user

**Example Success Response:**
```json
{
  "status": "success",
  "message": "User deleted",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** The response does not include a `data` field for delete operations.

---

## Event Endpoints

Base path: `/api/v1/events`  
**Authentication:** None required (SSE endpoint) / Internal API key for webhook

### GET /api/v1/events
Establish Server-Sent Events (SSE) connection for real-time document processing updates.

**Authentication:** None required  
**Content-Type:** `text/event-stream`

**Description:** This endpoint establishes a persistent SSE connection that allows the frontend to receive real-time updates about document processing status. The connection remains open and sends heartbeat events every 30 seconds to keep the connection alive.

**Event Types:**
- `heartbeat`: Periodic keep-alive event sent every 30 seconds
- `document_processing`: Document processing status updates

**Example Heartbeat Event:**
```
event: heartbeat
data: {"timestamp":"2024-01-01T12:00:00.000Z"}
```

**Example Document Processing Event:**
```
event: document_processing
data: {
  "documentId": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "status": "parsing_started",
  "message": "Document parsing has started",
  "metadata": {
    "filename": "technical_manual.pdf",
    "fileType": "pdf",
    "divisionId": "456e7890-e12b-34c5-d678-901234567890"
  }
}
```

**Status Values:**
- `parsing_started`: Document parsing has begun
- `parsing_failed`: Document parsing failed
- `embedding_started`: Embedding generation has started
- `embedding_completed`: Embedding generation completed
- `embedded`: Document fully processed and embedded

**Note:** The connection will automatically close if the client disconnects. The server handles cleanup automatically.

### POST /api/v1/events/webhook/document-processing
Receive document processing webhook from FastAPI ML service (internal API only).

**Authentication:** Internal API key required (`x-webhook-key` header)  
**Request Body:**
```json
{
  "documentId": "UUID (required)",
  "status": "string (required)",
  "message": "string (required)",
  "metadata": {
    "filename": "string (optional)",
    "fileType": "string (optional)",
    "divisionId": "UUID (optional)",
    "error": "string (optional)"
  }
}
```

**Example Request:**
```json
{
  "documentId": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "status": "embedded",
  "message": "Document successfully embedded",
  "metadata": {
    "filename": "technical_manual.pdf",
    "fileType": "pdf",
    "divisionId": "456e7890-e12b-34c5-d678-901234567890"
  }
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error": "Missing required fields: documentId, status",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Note:** This endpoint forwards the webhook event to all connected SSE clients via the SSE service.

---

# FastAPI ML Service (Port 8000)

Base URL: `http://localhost:8000`

## Health Check

### GET /health
Check the health status of the ML microservice.

**Authentication:** None required  

**Example Success Response:**
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
      "model": "all-MiniLM-L6-v2",
      "dimension": 384,
      "device": "cpu"
    },
    "rag_service": {
      "llm_model": "openai/gpt-oss-120b",
      "vector_db": "chromadb",
      "chunk_size": 512,
      "top_k": 5
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "message": "Service unhealthy",
  "error": "Database connection failed",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## Document Processing

### POST /parse-document
Parse and process an uploaded document (called by Express.js backend).

**Authentication:** None (internal service call)  
**Request Body:**
```json
{
  "document_id": "UUID (required)",
  "storage_path": "string (required) - Path in MinIO storage",
  "file_type": "string (required) - pdf|docx|txt|csv"
}
```

**Example Request:**
```json
{
  "document_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
  "file_type": "pdf"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Document parsing initiated successfully",
  "data": {
    "document_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "file_type": "pdf",
    "storage_path": "abc12345-def6-7890-ghij-klmnopqrstuv.pdf",
    "processing_status": "parsing_started",
    "estimated_completion": "2024-01-01T12:02:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "message": "Failed to parse document",
  "error": "File not found in storage",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Process:**
1. Downloads file from MinIO storage
2. Parses content based on file type
3. Chunks text into manageable segments
4. Generates embeddings using SentenceTransformers
5. Stores embeddings in ChromaDB and PostgreSQL
6. Updates document status in Express.js backend

---

## RAG Chat

### POST /chat
Process chat queries using Retrieval-Augmented Generation.

**Authentication:** None (typically called via Express.js proxy)  
**Request Body:**
```json
{
  "division_id": "UUID (required)",
  "query": "string (1-2000 chars, required)",
  "conversation_id": "UUID (optional)",
  "title": "string (optional)",
  "user_id": "UUID (optional)"
}
```

**Example Request:**
```json
{
  "division_id": "456e7890-e12b-34c5-d678-901234567890",
  "query": "How do I configure the database connection settings?",
  "conversation_id": "789e0123-e45f-67g8-h901-234567890123",
  "title": "Database Configuration Help",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Chat query processed successfully",
  "data": {
    "query": "How do I configure the database connection settings?",
    "answer": "To configure the database connection settings, you need to update the environment variables in your .env file. Set DATABASE_HOST to your PostgreSQL server address, DATABASE_PORT to 5432 (default), DATABASE_NAME to your database name, DATABASE_USER to your username, and DATABASE_PASSWORD to your password. For production environments, ensure you use strong passwords and consider using connection pooling for better performance.",
    "sources": [
      {
        "filename": "setup_guide.pdf",
        "chunk_index": 5,
        "distance": 0.18,
        "preview": "Database configuration requires setting up the following environment variables: DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD. The default port for PostgreSQL is 5432..."
      },
      {
        "filename": "deployment_manual.docx",
        "chunk_index": 12,
        "distance": 0.25,
        "preview": "For production deployments, always use strong passwords for database connections. Consider implementing connection pooling to improve performance and handle multiple concurrent requests..."
      },
      {
        "filename": "configuration_examples.txt",
        "chunk_index": 3,
        "distance": 0.29,
        "preview": "Example .env configuration: DATABASE_HOST=localhost, DATABASE_PORT=5432, DATABASE_NAME=myapp, DATABASE_USER=myuser, DATABASE_PASSWORD=securepassword123..."
      }
    ],
    "division_id": "456e7890-e12b-34c5-d678-901234567890",
    "model_used": "openai/gpt-oss-120b",
    "total_sources": 3,
    "conversation_id": "789e0123-e45f-67g8-h901-234567890123"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "message": "Failed to process chat query",
  "error": "No relevant documents found for the query",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Process:**
1. Generates query embedding
2. Performs vector similarity search in ChromaDB
3. Retrieves top-k relevant document chunks
4. Constructs prompt with context
5. Calls LLM (OpenRouter/OpenAI) for response generation
6. Returns answer with source citations

---

## Vector Database Management

Base path: `/vector`

### GET /vector/health
Get ChromaDB health status and statistics.

**Example Success Response:**
```json
{
  "success": true,
  "message": "ChromaDB health check completed",
  "data": {
    "status": "healthy",
    "total_collections": 1,
    "total_documents": 15,
    "total_embeddings": 342,
    "last_updated": "2024-01-01T11:45:00.000Z",
    "storage_used": "2.3MB",
    "performance_metrics": {
      "avg_query_time": "0.045s",
      "cache_hit_rate": "87%"
    }
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "ChromaDB health check failed",
  "data": {
    "status": "unhealthy",
    "error": "Connection timeout"
  }
}
```

### GET /vector/stats
Get detailed ChromaDB statistics.

**Example Success Response:**
```json
{
  "success": true,
  "message": "ChromaDB statistics retrieved successfully",
  "data": {
    "collections": [
      {
        "name": "chatbot_embeddings",
        "total_documents": 15,
        "total_embeddings": 342,
        "embedding_dimension": 384,
        "storage_size": "2.3MB",
        "last_updated": "2024-01-01T11:45:00.000Z"
      }
    ],
    "performance": {
      "total_queries": 1247,
      "avg_query_time": "0.045s",
      "cache_hit_rate": "87%",
      "memory_usage": "45MB"
    },
    "divisions": [
      {
        "division_id": "456e7890-e12b-34c5-d678-901234567890",
        "division_name": "Engineering",
        "document_count": 8,
        "embedding_count": 187,
        "active_documents": 6
      },
      {
        "division_id": "789e0123-e45f-67g8-h901-234567890123",
        "division_name": "Marketing",
        "document_count": 7,
        "embedding_count": 155,
        "active_documents": 5
      }
    ]
  }
}
```

### POST /vector/cleanup
Clean up all vector data from ChromaDB.

**Warning:** This removes all embeddings and cannot be undone.

**Example Success Response:**
```json
{
  "success": true,
  "message": "Successfully cleaned up ChromaDB vector data",
  "data": {
    "collections_removed": 1,
    "embeddings_deleted": 342,
    "storage_freed": "2.3MB",
    "cleanup_time": "0.234s"
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "Failed to cleanup ChromaDB data",
  "data": {
    "error": "Access denied - insufficient permissions"
  }
}
```

### DELETE /vector/document/:document_id
Delete all vectors for a specific document.

**Path Parameters:**
- `document_id`: UUID of the document

**Example Success Response:**
```json
{
  "success": true,
  "message": "Successfully deleted vectors for document abc12345-def6-7890-ghij-klmnopqrstuv",
  "data": {
    "document_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "embeddings_deleted": 23,
    "storage_freed": "156KB"
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "Failed to delete document vectors",
  "data": {
    "error": "Document not found in vector database"
  }
}
```

### DELETE /vector/division/:division_id
Delete all vectors for a specific division.

**Path Parameters:**
- `division_id`: UUID of the division

**Example Success Response:**
```json
{
  "success": true,
  "message": "Successfully deleted vectors for division 456e7890-e12b-34c5-d678-901234567890",
  "data": {
    "division_id": "456e7890-e12b-34c5-d678-901234567890",
    "documents_affected": 8,
    "embeddings_deleted": 187,
    "storage_freed": "1.2MB"
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "Failed to delete division vectors",
  "data": {
    "error": "Division not found or no vectors to delete"
  }
}
```

### PATCH /vector/document/:document_id/active
Update the active status of a document in ChromaDB.

**Path Parameters:**
- `document_id`: UUID of the document

**Query Parameters:**
- `is_active`: boolean (required) - New active status

**Example Success Response (Activation):**
```json
{
  "success": true,
  "message": "Successfully activated document abc12345-def6-7890-ghij-klmnopqrstuv in ChromaDB",
  "data": {
    "document_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "is_active": true,
    "embeddings_affected": 23,
    "updated_at": "2024-01-01T12:00:00.000Z"
  }
}
```

**Example Success Response (Deactivation):**
```json
{
  "success": true,
  "message": "Successfully deactivated document abc12345-def6-7890-ghij-klmnopqrstuv in ChromaDB",
  "data": {
    "document_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "is_active": false,
    "embeddings_affected": 23,
    "updated_at": "2024-01-01T12:00:00.000Z"
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "Failed to update document abc12345-def6-7890-ghij-klmnopqrstuv active status",
  "data": {
    "error": "Document embeddings not found in vector database"
  }
}
```

---

## Configuration

### Models and Services Used

**Embedding Model:** SentenceTransformers `all-MiniLM-L6-v2` (384 dimensions, local)  
**LLM Model:** OpenRouter `openai/gpt-oss-120b` (configurable)  
**Vector Database:** ChromaDB (persistent storage)  
**Object Storage:** MinIO (S3-compatible)  
**Primary Database:** PostgreSQL with pgvector extension

### Text Processing

**Chunk Size:** 512 tokens  
**Chunk Overlap:** 50 tokens  
**Top-K Results:** 5 (for RAG retrieval)  
**Max Query Length:** 2000 characters  
**Max LLM Response:** 1500 tokens

---

## Error Codes

**Express.js Backend:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate names)
- `500` - Internal Server Error

**FastAPI ML Service:**
- `200` - Success
- `400` - Bad Request
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Integration Flow

1. **Document Upload:**
   - Express.js receives file upload
   - Stores file in MinIO
   - Records metadata in PostgreSQL
   - Calls FastAPI `/parse-document` endpoint
   - FastAPI processes and embeds document
   - Updates status back to Express.js

2. **Chat Query:**
   - Express.js receives chat request
   - Validates user authentication
   - Proxies request to FastAPI `/chat`
   - FastAPI performs RAG pipeline
   - Returns response through Express.js

3. **Document Management:**
   - Express.js handles CRUD operations
   - Calls FastAPI vector endpoints for cleanup
   - Maintains data consistency across services

This architecture separates concerns effectively: Express.js handles business logic, authentication, and data management, while FastAPI focuses on ML operations, document processing, and vector search capabilities.
