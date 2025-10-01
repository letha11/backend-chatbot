## Product Requirements Document: Chatbot Control Panel with Document Management

This document details the features for Phases 2, 3, and 4 of the Chatbot Control Panel with Document Management project. We will be using a hybrid backend approach: Express.js (TypeScript) for core CRUD operations, authentication, and general API handling, and FastAPI (Python) for embedding generation and retrieval, acting as a microservice.

---

### Phase 2: Database & Storage Setup

**Feature 2.1: PostgreSQL with `pgvector` Extension**

*   **Description:** Initialize a PostgreSQL database instance and enable the `pgvector` extension to support vector similarity search for embeddings. This will serve as the primary data store for all application metadata and document embeddings.
*   **User Stories:**
    *   As a developer, I need a PostgreSQL database with `pgvector` enabled so that I can store document metadata and vector embeddings in a unified manner.
*   **Technical Specifications:**
    *   **Database:** PostgreSQL 14+
    *   **Extension:** `pgvector`
    *   **Configuration:** Ensure appropriate database credentials and connection pooling settings are configured.
    *   **Deployment:** Instructions for local setup and potential cloud provider setup (e.g., AWS RDS, Azure Database for PostgreSQL).
*   **Acceptance Criteria:**
    *   A PostgreSQL instance is running and accessible.
    *   The `pgvector` extension is successfully enabled and functional (verified by creating a test table with a `vector` column).

**Feature 2.2: Database Schema Creation**

*   **Description:** Define and create the necessary tables in the PostgreSQL database to store information about divisions, documents, embeddings, and user queries. This feature establishes the data model for the application.
*   **User Stories:**
    *   As a developer, I need predefined tables for `division`, `document`, `embedding`, and `user_query` to structure the application's data correctly.
*   **Technical Specifications:**
    *   **Table: `divisions`**
        *   `id` (UUID, Primary Key)
        *   `name` (VARCHAR(255), NOT NULL, UNIQUE)
        *   `description` (TEXT, NULL)
        *   `is_active` (BOOLEAN, DEFAULT TRUE)
        *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
        *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   **Table: `documents`**
        *   `id` (UUID, Primary Key)
        *   `division_id` (UUID, Foreign Key REFERENCES `divisions(id)`, NOT NULL)
        *   `original_filename` (VARCHAR(255), NOT NULL)
        *   `storage_path` (VARCHAR(255), NOT NULL) - Path to the raw file in object storage.
        *   `file_type` (VARCHAR(50), NOT NULL) - e.g., 'pdf', 'docx', 'txt', 'csv'.
        *   `status` (VARCHAR(50), NOT NULL, DEFAULT 'uploaded') - e.g., 'uploaded', 'parsed', 'embedded', 'failed'.
        *   `is_active` (BOOLEAN, DEFAULT FALSE) - Determines if the document is used for retrieval.
        *   `uploaded_by` (UUID, Foreign Key REFERENCES `users(id)`, NULL) - Assuming a `users` table for admins.
        *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
        *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   **Table: `embeddings`**
        *   `id` (UUID, Primary Key)
        *   `document_id` (UUID, Foreign Key REFERENCES `documents(id)`, NOT NULL)
        *   `chunk_text` (TEXT, NOT NULL) - The actual text chunk that was embedded.
        *   `embedding` (VECTOR(384), NOT NULL) - Vector representation of the chunk (384 for SentenceTransformers `all-MiniLM-L6-v2`).
        *   `chunk_index` (INTEGER, NOT NULL) - Order of the chunk within the document.
        *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   **Table: `user_queries`** (Optional for Phase 2, but good for future analytics)
        *   `id` (UUID, Primary Key)
        *   `division_id` (UUID, Foreign Key REFERENCES `divisions(id)`, NULL)
        *   `query_text` (TEXT, NOT NULL)
        *   `response_text` (TEXT, NULL)
        *   `query_time` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
        *   `user_id` (UUID, NULL) - If authenticated users.
    *   **Table: `users`** (Basic for authentication in Phase 3)
        *   `id` (UUID, Primary Key)
        *   `username` (VARCHAR(255), NOT NULL, UNIQUE)
        *   `password_hash` (VARCHAR(255), NOT NULL)
        *   `role` (VARCHAR(50), DEFAULT 'admin') - e.g., 'admin', 'super_admin'.
        *   `is_active` (BOOLEAN, DEFAULT TRUE)
        *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
        *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
*   **Acceptance Criteria:**
    *   All specified tables are created in the database with correct column types, constraints, and foreign key relationships.
    *   A schema migration tool (e.g., `TypeORM Migrations` for Express.js with TypeORM, or `node-pg-migrate`) is configured to manage schema changes.

**Feature 2.3: Object Storage Integration**

*   **Description:** Integrate with an object storage service (e.g., AWS S3, MinIO) to store raw uploaded document files. This ensures scalability and separates large binary data from the database.
*   **User Stories:**
    *   As an administrator, I need a reliable place to store the original document files so that they can be retrieved for parsing or re-processing.
    *   As a system, I need to store raw uploaded files externally to keep the database lean and efficient.
*   **Technical Specifications:**
    *   **Service:** AWS S3, MinIO, or compatible S3-like storage.
    *   **Configuration:**
        *   Access Key ID
        *   Secret Access Key
        *   Region (for S3)
        *   Bucket Name
        *   Endpoint (for MinIO or custom S3-compatible)
    *   **API Client:** Use an appropriate SDK (e.g., AWS SDK for JavaScript, `minio` client) in the Express.js backend.
    *   **File Naming Convention:** Store files with a UUID as their name (e.g., `document_id.file_extension`) to prevent naming conflicts.
*   **Acceptance Criteria:**
    *   The Express.js backend can successfully connect to the configured object storage.
    *   The backend can upload a test file to the specified bucket/storage.
    *   The backend can retrieve and delete a test file from the specified bucket/storage.

**Feature 2.4: Basic SQL Migrations**

*   **Description:** Implement a robust database migration system to manage schema changes and ensure consistency across environments.
*   **User Stories:**
    *   As a developer, I need a way to apply schema changes in a controlled and repeatable manner so that the database structure remains consistent across development, staging, and production environments.
*   **Technical Specifications:**
    *   **Tool:** `TypeORM Migrations` (if using TypeORM), or a standalone tool like `node-pg-migrate`.
    *   **Migration Scripts:** Create initial migration scripts to set up all tables defined in Feature 2.2.
    *   **Workflow:** Define a clear workflow for creating, running, and reverting migrations.
*   **Acceptance Criteria:**
    *   A migration tool is integrated into the project.
    *   Initial migration scripts exist and can successfully create the database schema from scratch.
    *   Migration scripts can be run and rolled back without errors.

---

### Phase 3: Backend Foundations (Express.js)

**Feature 3.1: Project Setup & Structure**

*   **Description:** Initialize the Express.js project with TypeScript, establish a clear project structure, and configure essential development tools.
*   **User Stories:**
    *   As a developer, I need a well-structured Express.js project with TypeScript so that I can easily develop, maintain, and scale the backend.
*   **Technical Specifications:**
    *   **Framework:** Express.js
    *   **Language:** TypeScript
    *   **ORM (Recommended):** TypeORM or Prisma for database interaction.
    *   **Project Structure (Example):**
        *   `src/`
            *   `app.ts` (main application entry)
            *   `config/` (database, environment variables, object storage config)
            *   `controllers/` (API logic)
            *   `middlewares/` (authentication, error handling)
            *   `models/` (TypeORM entities/Prisma schema)
            *   `routes/` (API endpoint definitions)
            *   `services/` (business logic, database operations)
            *   `utils/` (helper functions)
        *   `tests/`
        *   `migrations/`
    *   **Dependency Management:** `npm` or `yarn`.
    *   **Linting/Formatting:** ESLint, Prettier.
    *   **Build:** `tsc` for TypeScript compilation.
*   **Acceptance Criteria:**
    *   A TypeScript Express.js project is initialized and runs successfully.
    *   A logical project structure is established.
    *   Basic database connection (e.g., via TypeORM) is configured and tested.

**Feature 3.2: User Authentication (JWT-based)**

*   **Description:** Implement user registration (for initial admins), login, and JWT-based authentication to secure API endpoints. Only authenticated administrators can access CRUD operations for divisions and documents.
*   **User Stories:**
    *   As an administrator, I need to securely log in to the system so that I can access and manage divisions and documents.
    *   As a system, I need to verify the identity of users accessing administrative endpoints to ensure data integrity and security.
*   **Technical Specifications:**
    *   **Strategy:** JSON Web Tokens (JWT).
    *   **Hashing:** `bcrypt` for password hashing.
    *   **Endpoints:**
        *   `POST /auth/register`: Create a new admin user (initially, this might be a one-time script or only accessible by a super-admin for setup).
            *   **Request:** `{ username, password, role }`
            *   **Response:** `{ message: "User registered successfully" }`
        *   `POST /auth/login`: Authenticate a user and return a JWT.
            *   **Request:** `{ username, password }`
            *   **Response:** `{ token: "...", user: { id, username, role } }`
        *   `GET /auth/me`: (Optional) Get current authenticated user details.
            *   **Requires:** `Authorization: Bearer <token>`
            *   **Response:** `{ id, username, role }`
    *   **Middleware:** An Express.js middleware to validate JWTs on protected routes.
    *   **Error Handling:** Proper error responses for invalid credentials, missing tokens, etc.
*   **Acceptance Criteria:**
    *   A user can register (if registration is exposed).
    *   A user can successfully log in and receive a JWT.
    *   Protected API routes return a `401 Unauthorized` without a valid JWT.
    *   Protected API routes allow access with a valid JWT.
    *   Passwords are securely hashed in the database.

**Feature 3.3: Division Management Endpoints**

*   **Description:** Implement CRUD (Create, Read, Update, Delete) API endpoints for managing divisions. These endpoints will be protected by authentication.
*   **User Stories:**
    *   As an administrator, I need to create new divisions so that I can categorize documents for different teams or topics.
    *   As an administrator, I need to view existing divisions to understand the current structure.
    *   As an administrator, I need to update division details (name, description, active status) to keep information current.
    *   As an administrator, I need to delete divisions (soft delete preferred) to remove outdated categories.
*   **Technical Specifications:**
    *   **Base Path:** `/api/v1/divisions`
    *   **Endpoints (Protected by JWT):**
        *   `POST /`: Create a new division.
            *   **Request:** `{ name: string, description?: string, is_active?: boolean }`
            *   **Response:** `201 Created`, `{ id, name, description, is_active, created_at, updated_at }`
        *   `GET /`: Get all divisions.
            *   **Response:** `200 OK`, `[{ id, name, description, is_active, created_at, updated_at }, ...]`
        *   `GET /:id`: Get a single division by ID.
            *   **Response:** `200 OK`, `{ id, name, description, is_active, created_at, updated_at }` or `404 Not Found`.
        *   `PUT /:id`: Update an existing division.
            *   **Request:** `{ name?: string, description?: string, is_active?: boolean }`
            *   **Response:** `200 OK`, `{ id, name, description, is_active, created_at, updated_at }` or `404 Not Found`.
        *   `DELETE /:id`: Soft delete a division (e.g., set `is_active = false` or a `deleted_at` timestamp).
            *   **Response:** `204 No Content` or `200 OK`, `{ message: "Division deactivated/deleted successfully" }`
    *   **Validation:** Input validation for request bodies (e.g., `name` is required, `is_active` is boolean).
    *   **Database Interaction:** Use TypeORM/Prisma to interact with the `divisions` table.
*   **Acceptance Criteria:**
    *   Administrators can successfully create, retrieve, update, and (soft) delete divisions via API calls.
    *   Appropriate HTTP status codes are returned for success and error scenarios.
    *   All division management endpoints are protected by JWT authentication.

**Feature 3.4: Document Management Endpoints**

*   **Description:** Implement API endpoints for uploading, toggling the active status, and deleting/soft deleting documents. This involves interaction with both the PostgreSQL database and object storage.
*   **User Stories:**
    *   As an administrator, I need to upload new document files to a specific division so that they can be used by the chatbot.
    *   As an administrator, I need to activate or deactivate documents so that I can control which documents the chatbot uses for answering queries.
    *   As an administrator, I need to delete documents so that I can remove outdated or incorrect information.
    *   As an administrator, I need to view a list of all documents, optionally filtered by division, to monitor the available knowledge base.
*   **Technical Specifications:**
    *   **Base Path:** `/api/v1/documents`
    *   **Endpoints (Protected by JWT):**
        *   `POST /upload`: Upload a new document.
            *   **Requires:** `multipart/form-data`
            *   **Request:** `file` (the document itself), `division_id: string`
            *   **Process:**
                1.  Validate `division_id`.
                2.  Store the raw file in object storage (e.g., S3).
                3.  Record document metadata (filename, path, type, `status='uploaded'`, `is_active=false`) in the `documents` table.
                4.  Trigger asynchronous processing for parsing and embedding (see Phase 4).
            *   **Response:** `201 Created`, `{ id, division_id, original_filename, storage_path, file_type, status, is_active, created_at }`
        *   `GET /`: Get all documents (optionally filterable).
            *   **Query Params:** `division_id?: string`, `is_active?: boolean`
            *   **Response:** `200 OK`, `[{ id, original_filename, division_id, file_type, status, is_active, ... }, ...]`
        *   `GET /:id`: Get a single document by ID.
            *   **Response:** `200 OK`, `{ id, original_filename, division_id, file_type, status, is_active, ... }` or `404 Not Found`.
        *   `PATCH /:id/toggle`: Toggle the `is_active` status of a document.
            *   **Request:** `{ is_active: boolean }`
            *   **Response:** `200 OK`, `{ id, is_active, ... }` or `404 Not Found`.
        *   `DELETE /:id`: Soft delete a document (e.g., update `status='deleted'` and set `is_active=false`). Optionally remove from object storage.
            *   **Process:**
                1.  Update document status in DB.
                2.  Remove associated embeddings from the `embeddings` table.
                3.  (Optional, but recommended) Delete the raw file from object storage.
            *   **Response:** `204 No Content` or `200 OK`, `{ message: "Document deleted successfully" }`
    *   **File Handling:** Use `multer` for Express.js to handle `multipart/form-data` file uploads.
    *   **Object Storage Integration:** Use the S3/MinIO client from Feature 2.3.
    *   **Database Interaction:** Use TypeORM/Prisma for the `documents` table.
*   **Acceptance Criteria:**
    *   Administrators can successfully upload documents to object storage and record their metadata in the database via the API.
    *   Administrators can activate/deactivate documents, and this status is reflected in the database.
    *   Administrators can list documents, with filtering options.
    *   Administrators can (soft) delete documents, which also removes associated embeddings and optionally the raw file.
    *   All document management endpoints are protected by JWT authentication.

**Feature 3.5: Basic File Parsing (Microservice Call)**

*   **Description:** When a document is uploaded, the Express.js backend will trigger a call to the FastAPI Python microservice to initiate the parsing process. The Express.js backend does *not* directly perform parsing.
*   **User Stories:**
    *   As a system, I need to initiate the parsing of uploaded documents so that their content can be extracted for embedding.
*   **Technical Specifications:**
    *   **Trigger:** Upon successful document upload and metadata storage in Feature 3.4.
    *   **Communication:** Express.js backend makes an HTTP POST request to a dedicated FastAPI endpoint (e.g., `POST /parse-document`).
    *   **Request Body (to FastAPI):** `{ document_id: UUID, storage_path: string, file_type: string }`
    *   **Response (from FastAPI):** FastAPI should return a success status (e.g., 202 Accepted) indicating that parsing has started asynchronously.
    *   **Error Handling:** If the call to FastAPI fails, log the error and update the document status in the Express.js database to `status='parsing_failed'`.
*   **Acceptance Criteria:**
    *   After uploading a document, the Express.js backend successfully sends a request to the FastAPI microservice to initiate parsing.
    *   The Express.js backend handles successful and failed responses from the FastAPI parsing endpoint.

---

### Phase 4: Embedding & Retrieval (FastAPI Python Microservice)

**Feature 4.1: FastAPI Microservice Setup**

*   **Description:** Initialize the FastAPI project with Python, establish its structure, and configure necessary dependencies for parsing, embedding, and database interaction. This will run as a separate service from the Express.js backend.
*   **User Stories:**
    *   As a developer, I need a dedicated Python microservice for handling complex tasks like document parsing, embedding generation, and vector search, to leverage Python's ecosystem for NLP.
*   **Technical Specifications:**
    *   **Framework:** FastAPI
    *   **Language:** Python
    *   **Dependencies:**
        *   `uvicorn` (ASGI server)
        *   `psycopg2-binary` or `asyncpg` (PostgreSQL client)
        *   `openai` (for OpenAI embeddings) or `sentence-transformers` (for local models)
        *   `pdfminer.six` or `PyPDF2` (for PDF parsing)
        *   `python-docx` (for DOCX parsing)
        *   `pandas` (for CSV parsing)
        *   `boto3` or `minio` (for object storage access)
    *   **Project Structure (Example):**
        *   `app/`
            *   `main.py` (FastAPI entry point)
            *   `config.py` (environment variables, API keys)
            *   `db.py` (database connection)
            *   `services/`
                *   `parser.py` (document parsing logic)
                *   `embedder.py` (embedding generation logic)
                *   `retriever.py` (vector search logic)
            *   `models.py` (Pydantic models for API requests/responses)
        *   `requirements.txt`
*   **Acceptance Criteria:**
    *   A FastAPI application is initialized and runs successfully (e.g., via `uvicorn`).
    *   All necessary Python dependencies are installed.
    *   The FastAPI service can connect to the shared PostgreSQL database and object storage.

**Feature 4.2: Document Parsing & Chunking**

*   **Description:** Implement logic within the FastAPI microservice to retrieve raw document files from object storage, parse their content into plain text, and then chunk this text into manageable segments suitable for embedding.
*   **User Stories:**
    *   As a system, I need to parse various document types into readable text so that their content can be processed.
    *   As a system, I need to split large documents into smaller, meaningful chunks to improve the accuracy and efficiency of embedding and retrieval.
*   **Technical Specifications:**
    *   **Endpoint:** `POST /parse-document` (called by Express.js)
        *   **Request:** `{ document_id: UUID, storage_path: string, file_type: string }`
        *   **Process:**
            1.  Retrieve raw file from object storage using `storage_path`.
            2.  **File Parsing:**
                *   `TXT`: Read raw text.
                *   `PDF`: Use `pdfminer.six` or `PyPDF2` to extract text. Handle layout and tables.
                *   `DOCX`: Use `python-docx` to extract text.
                *   `CSV`: Read with `pandas`, convert to a readable string format (e.g., JSON representation or descriptive text).
            3.  **Text Chunking:**
                *   Split the parsed text into chunks (e.g., 512 tokens with some overlap).
                *   Strategy: Recursive character text splitter, NLTK Sentence tokenizer + fixed chunk size, or similar.
            4.  Update document status in Express.js database (via Express.js API call or direct DB update) to `status='parsed'`.
            5.  Trigger Feature 4.3 (embedding generation) for each chunk.
    *   **Error Handling:** Handle malformed files, unsupported file types, and parsing errors. Update document status to `status='parsing_failed'`.
*   **Acceptance Criteria:**
    *   The FastAPI service can successfully retrieve files from object storage.
    *   The FastAPI service can parse TXT, PDF, DOCX, and CSV files into plain text.
    *   Parsed text is accurately chunked into smaller segments.
    *   The document status in the main database is updated to `parsed` upon successful parsing.
    *   Errors during parsing are logged, and the document status is updated to `parsing_failed`.

**Feature 4.3: Embedding Generation**

*   **Description:** Generate vector embeddings for each text chunk using a chosen embedding model (e.g., OpenAI, SentenceTransformers) and store them in the `embeddings` table of the PostgreSQL database.
*   **User Stories:**
    *   As a system, I need to convert text chunks into numerical vector representations so that they can be used for similarity search.
*   **Technical Specifications:**
    *   **Trigger:** After successful chunking from Feature 4.2.
    *   **Embedding Model:**
        *   **Option 1 (Recommended for simplicity):** OpenAI `text-embedding-ada-002` (requires OpenAI API key).
        *   **Option 2:** SentenceTransformers (e.g., `all-MiniLM-L6-v2`) for local model inference.
    *   **Process:**
        1.  For each chunk generated in Feature 4.2:
            *   Call the embedding model API/function to get the vector.
            *   Store `document_id`, `chunk_text`, `embedding` (the vector), and `chunk_index` in the `embeddings` table.
        2.  After all chunks for a document are embedded, update the `documents` table (via Express.js API call or direct DB update) to set `status='embedded'`.
    *   **Error Handling:** Handle API errors, rate limits, or model inference failures. Update document status to `status='embedding_failed'`.
*   **Acceptance Criteria:**
    *   Embeddings are successfully generated for each document chunk.
    *   Embeddings are stored correctly in the `embeddings` table, associated with their `document_id` and `chunk_text`.
    *   The `documents.status` field is updated to `embedded` upon successful completion.
    *   Errors during embedding generation are logged, and the document status is updated to `embedding_failed`.

**Feature 4.4: Chat Retrieval Endpoint (RAG Pipeline)**

*   **Description:** Implement the core RAG (Retrieval Augmented Generation) pipeline within the FastAPI microservice. This endpoint will receive a user query, retrieve relevant document chunks using vector similarity search, construct a prompt, and send it to an LLM to generate an answer.
*   **User Stories:**
    *   As a user, I need to ask a question to the chatbot for a specific division and receive an answer based on the active documents in that division.
*   **Technical Specifications:**
    *   **Endpoint:** `POST /chat`
        *   **Request:** `{ division_id: UUID, query: string }`
        *   **Process:**
            1.  **Query Embedding:** Generate an embedding for the `user_query` using the same embedding model as Feature 4.3.
            2.  **Retrieval:**
                *   Perform a similarity search in the `embeddings` table:
                    *   Filter by `document_id` where `document.division_id = :division_id` AND `document.is_active = TRUE` AND `document.status = 'embedded'`.
                    *   Use `pgvector`'s `<=>` operator (cosine distance) to find the top `K` most similar `embedding` vectors to the `query_embedding`.
                *   Retrieve the `chunk_text` for these top `K` embeddings.
            3.  **Prompt Construction:**
                *   Combine the retrieved `chunk_text` with the `user_query` into a well-structured prompt for an LLM.
                *   Example prompt structure:
                    ```
                    You are a helpful assistant. Use the following context to answer the question.
                    If you don't know the answer, state that you don't have enough information.

                    Context:
                    [Chunk 1 Text]
                    [Chunk 2 Text]
                    ...
                    [Chunk K Text]

                    Question: [User Query]
                    Answer:
                    ```
            4.  **LLM Call:** Send the constructed prompt to an LLM (e.g., OpenAI GPT series).
            5.  **Response:** Return the LLM's generated answer.
            6.  **(Optional):** Record `user_query`, `division_id`, and `response_text` in the `user_queries` table.
*   **Acceptance Criteria:**
    *   The `/chat` endpoint successfully receives a user query and division ID.
    *   The user query is embedded.
    *   Relevant document chunks are retrieved from the database, correctly filtered by `division_id` and `is_active=TRUE` status.
    *   A coherent prompt is constructed from the query and retrieved chunks.
    *   An LLM generates an answer based on the prompt.
    *   The LLM's answer is returned as the API response.
    *   Queries and responses are optionally logged in the `user_queries` table.
