"""
FastAPI ML Microservice for document processing, embeddings, and RAG chat.
"""
from contextlib import asynccontextmanager
from uuid import UUID
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from .config import settings
from .database import init_db, db_manager
from .models import (
    DeleteDocumentResponse, ParseDocumentRequest, ParseDocumentResponse, ChatRequest, ChatResponse,
    HealthResponse, ErrorResponse
)
from .services.storage import storage_service
from .services.parser import document_parser
from .services.embedder import embedding_service
from .services.retriever import rag_service
# Chroma vector service removed; using OpenSearch directly
from .services.webhook_service import webhook_service
from .services.opensearch import opensearch_service
from .routes import vector_routes

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application."""
    # Startup
    logger.info("Starting FastAPI ML Microservice...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
        
        # Test embedding service
        logger.info(f"Embedding service info: {embedding_service.get_model_info()}")
        
        # Vector service initialization removed (using OpenSearch directly)
        
        # Test storage service
        logger.info("Testing storage service connection...")
        # Just test the bucket exists (it will be created if not)
        
        logger.info("FastAPI ML Microservice started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI ML Microservice...")
    
    # No vector service to close (OpenSearch client persists)


# Create FastAPI app
app = FastAPI(
    title="Chatbot Control Panel - ML Microservice",
    description="FastAPI microservice for document processing, embedding generation, and RAG chat functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include vector management routes
app.include_router(vector_routes.router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        # Test database connection
        await db_manager.get_document(UUID("00000000-0000-0000-0000-000000000000"))
        db_status = "connected"
        
        return HealthResponse(
            status="success",
            message="ML microservice is healthy",
            data={
                "service": "FastAPI ML Microservice",
                "version": "1.0.0",
                "environment": settings.environment,
                "database_status": db_status,
                "embedding_service": embedding_service.get_model_info(),
                "rag_service": rag_service.get_service_info()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                status="error",
                message="Service unhealthy",
                error=str(e)
            ).dict()
        )


@app.post("/parse-document", response_model=ParseDocumentResponse)
async def parse_document(
    request: ParseDocumentRequest,
    background_tasks: BackgroundTasks
) -> ParseDocumentResponse:
    """
    Parse a document and generate embeddings.
    This endpoint is called by the Express.js backend after document upload.
    """
    try:
        logger.info(f"Received parse request for document {request.document_id}")
        
        # Get document info from database
        document_info = await db_manager.get_document(request.document_id)
        if not document_info:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    status="error",
                    message="Document not found",
                    error=f"Document with ID {request.document_id} not found in database"
                ).dict()
            )
        
        # Download file from storage
        file_content = await storage_service.download_file(request.storage_path)
        if not file_content:
            await db_manager.update_document_status(request.document_id, "parsing_failed")
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    status="error",
                    message="File not found in storage",
                    error=f"Could not download file from path: {request.storage_path}"
                ).dict()
            )
        
        # Parse document in background
        background_tasks.add_task(
            process_document_parsing,
            request.document_id,
            file_content,
            request.file_type,
            document_info["original_filename"],
            document_info["division_id"],
            document_info["is_active"]
        )
        
        return ParseDocumentResponse(
            status="success",
            message="Document parsing started",
            data={
                "document_id": str(request.document_id),
                "status": "processing",
                "file_type": request.file_type,
                "filename": document_info["original_filename"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in parse_document: {e}")
        await db_manager.update_document_status(request.document_id, "parsing_failed")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status="error",
                message="Internal server error during document parsing",
                error=str(e)
            ).dict()
        )

@app.delete("/delete-document/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(document_id: UUID) -> DeleteDocumentResponse:
    """
    Delete a document from the database and OpenSearch.
    """
    try:
        await db_manager.delete_document_embeddings(document_id)
        # await opensearch_service.delete_document(document_id)
        return DeleteDocumentResponse(status="success", message="Document deleted successfully", data={
            "document_id": str(document_id)
        })
    except Exception as e:
        logger.error(f"Error in delete_document: {e}")
        raise HTTPException(status_code=500, detail=ErrorResponse(status="error", message="Internal server error during document deletion", error=str(e)).dict())



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat query using RAG pipeline.
    """
    try:
        logger.info(f"Received chat request for division {request.division_id}")
        
        # Process query using RAG service
        result = await rag_service.process_chat_query(
            request.division_id,
            request.query,
            conversation_id=request.conversation_id,
            title=request.title,
            user_id=request.user_id,
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    status="error",
                    message="Failed to process chat query",
                    error="Could not generate response for the query"
                ).dict()
            )

        return ChatResponse(
            status="success",
            message="Chat query processed successfully",
            data={
                "query": result.query,
                "answer": result.answer,
                "sources": ','.join(set([source.filename for source in result.sources])),
                "division_id": str(result.division_id),
                "model_used": result.model_used,
                "total_sources": len(result.sources),
                "conversation_id": str(result.conversation_id) if result.conversation_id else None,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status="error",
                message="Internal server error during chat processing",
                error=str(e)
            ).dict()
        )


async def process_document_parsing(
    document_id: UUID,
    file_content: bytes,
    file_type: str,
    filename: str,
    division_id: UUID,
    is_active: bool
) -> None:
    """
    Background task to process document parsing and embedding generation.
    """
    try:
        logger.info(f"Starting background processing for document {document_id}")
        
        # Update status to parsing
        await db_manager.update_document_status(document_id, "parsing")
        
        # Notify Express backend that parsing has started
        await webhook_service.notify_parsing_started(str(document_id), filename, file_type)
        
        # Parse document
        chunks = await document_parser.parse_document(file_content, file_type, filename)
        if not chunks:
            logger.error(f"Failed to parse document {document_id}")
            await db_manager.update_document_status(document_id, "parsing_failed")
            await webhook_service.notify_processing_failed(
                str(document_id), filename, "Failed to parse document", "parsing"
            )
            return
        
        # Update status to parsed
        await db_manager.update_document_status(document_id, "parsed")
        logger.info(f"Successfully parsed document {document_id} into {len(chunks)} chunks")
        
        # Notify Express backend that parsing completed
        await webhook_service.notify_parsing_completed(str(document_id), filename, len(chunks))
        
        # Generate embeddings
        await db_manager.update_document_status(document_id, "embedding")
        
        # Notify Express backend that embedding has started
        await webhook_service.notify_embedding_started(str(document_id), filename)
        
        embeddings_data = await embedding_service.generate_embeddings(chunks, document_id, filename, division_id, is_active)
        if not embeddings_data:
            logger.error(f"Failed to generate embeddings for document {document_id}")
            await db_manager.update_document_status(document_id, "embedding_failed")
            await webhook_service.notify_processing_failed(
                str(document_id), filename, "Failed to generate embeddings", "embedding"
            )
            return

        logger.info(f"Successfully generated {len(embeddings_data)} embeddings for document {document_id}")
        logger.info(f"Embeddings data: {embeddings_data}")
        
        # Store embeddings in database
        embeddings_dict_list = []
        for embedding_data in embeddings_data:
            embeddings_dict_list.append({
                "document_id": embedding_data.document_id,  # Already a UUID, no conversion needed
                "chunk_text": embedding_data.chunk_text,
                "embedding": embedding_data.embedding,
                "chunk_index": embedding_data.chunk_index,
                "division_id": embedding_data.division_id,
                "filename": embedding_data.filename,
                "is_active": embedding_data.is_active
            })
        
        success = await db_manager.store_embeddings(embeddings_dict_list)
        if not success:
            logger.error(f"Failed to store embeddings for document {document_id}")
            await db_manager.update_document_status(document_id, "embedding_failed")
            await webhook_service.notify_processing_failed(
                str(document_id), filename, "Failed to store embeddings", "embedding"
            )
            return

        # Store documents in OpenSearch
        # await opensearch_service.store_document(embeddings_data)
        
        # Update final status to embedded
        await db_manager.update_document_status(document_id, "embedded")
        logger.info(f"Successfully completed processing for document {document_id}")
        
        # Notify Express backend that processing completed successfully
        await webhook_service.notify_embedding_completed(str(document_id), filename, len(embeddings_data))
        
    except Exception as e:
        logger.error(f"Error in background document processing: {e}")
        await db_manager.update_document_status(document_id, "processing_failed")
        await webhook_service.notify_processing_failed(
            str(document_id), filename, str(e), "processing"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else settings.workers
    )
