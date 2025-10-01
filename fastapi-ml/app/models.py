"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# Request Models
class ParseDocumentRequest(BaseModel):
    """Request model for document parsing."""
    document_id: UUID = Field(..., description="UUID of the document to parse")
    storage_path: str = Field(..., description="Path to the document in object storage")
    file_type: str = Field(..., description="Type of the file (pdf, docx, txt, csv)")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    division_id: UUID = Field(..., description="UUID of the division to search in")
    query: str = Field(..., min_length=1, max_length=2000, description="User query text")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID to continue")
    title: Optional[str] = Field(None, description="Conversation title when starting a new conversation")
    user_id: Optional[UUID] = Field(None, description="Optional user identifier for attribution")


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    document_id: UUID = Field(..., description="UUID of the document")
    chunks: List[str] = Field(..., description="List of text chunks to embed")


# Response Models
class StandardResponse(BaseModel):
    """Standard response format."""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ParseDocumentResponse(StandardResponse):
    """Response model for document parsing."""
    data: Optional[Dict[str, Any]] = Field(None, description="Parsing result data")


class ChatResponse(StandardResponse):
    """Response model for chat endpoint."""
    data: Optional[Dict[str, Any]] = Field(None, description="Chat response data")


class EmbeddingResponse(StandardResponse):
    """Response model for embedding generation."""
    data: Optional[Dict[str, Any]] = Field(None, description="Embedding generation result")


class HealthResponse(StandardResponse):
    """Response model for health check."""
    data: Dict[str, Any] = Field(..., description="Health check data")


class ErrorResponse(StandardResponse):
    """Response model for errors."""
    error: str = Field(..., description="Error description")
    errors: Optional[List[str]] = Field(None, description="Detailed error messages")


# Internal Data Models
class DocumentChunk(BaseModel):
    """Model for document text chunks."""
    text: str = Field(..., description="Chunk text content")
    index: int = Field(..., description="Chunk index in the document")
    start_char: Optional[int] = Field(None, description="Starting character position")
    end_char: Optional[int] = Field(None, description="Ending character position")


class EmbeddingData(BaseModel):
    """Model for embedding data."""
    document_id: UUID = Field(..., description="Document UUID")
    chunk_text: str = Field(..., description="Text that was embedded")
    embedding: List[float] = Field(..., description="Vector embedding")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    
    # Optional fields for vector database metadata
    division_id: Optional[UUID] = Field(None, description="Division UUID for filtering")
    filename: Optional[str] = Field(None, description="Original filename")
    is_active: Optional[bool] = Field(None, description="Whether the document is active")
    document_status: Optional[str] = Field(None, description="Document processing status")


class SimilarChunk(BaseModel):
    """Model for similar chunks from vector search."""
    chunk_text: str = Field(..., description="Text content of the chunk")
    chunk_index: int = Field(..., description="Index of the chunk")
    filename: str = Field(..., description="Original filename of the document")
    distance: float = Field(..., description="Vector distance (lower is more similar)")


class ParseResult(BaseModel):
    """Model for document parsing results."""
    document_id: UUID = Field(..., description="Document UUID")
    chunks: List[DocumentChunk] = Field(..., description="Extracted text chunks")
    total_chunks: int = Field(..., description="Total number of chunks")
    file_type: str = Field(..., description="Type of the processed file")
    original_filename: str = Field(..., description="Original filename")


class ChatResult(BaseModel):
    """Model for chat response results."""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SimilarChunk] = Field(..., description="Source chunks used for the answer")
    division_id: UUID = Field(..., description="Division ID that was searched")
    model_used: str = Field(..., description="LLM model used for generation")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID for subsequent turns")


# Configuration Models
class ModelConfig(BaseModel):
    """Model configuration settings."""
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")
    llm_model: str = Field(..., description="LLM model name")
    chunk_size: int = Field(..., description="Text chunk size")
    chunk_overlap: int = Field(..., description="Chunk overlap size")
    top_k_results: int = Field(..., description="Number of results to retrieve")
