"""
Database connection and models for the FastAPI ML microservice.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text, Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import uuid
from loguru import logger

from .config import settings

# Create both sync and async engines
sync_engine = create_engine(settings.database_url)
async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()


class Document(Base):
    """Document model for accessing document metadata."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    division_id = Column(UUID(as_uuid=True), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")
    is_active = Column(Boolean, default=False)
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Embedding table removed - using OpenSearch for vector storage


class UserQuery(Base):
    """User query model for logging chat interactions."""
    __tablename__ = "user_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    division_id = Column(UUID(as_uuid=True), nullable=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    query_time = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), nullable=True)


# Database dependency for sync operations
def get_db() -> Session:
    """Get synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database dependency for async operations
async def get_async_db() -> AsyncSession:
    """Get asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """Database operations manager."""
    
    @staticmethod
    async def update_document_status(document_id: uuid.UUID, status: str) -> bool:
        """Update document status in the database."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("UPDATE documents SET status = :status, updated_at = NOW() WHERE id = :document_id"),
                    {"status": status, "document_id": document_id}
                )
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating document status: {e}")
            return False
    
    @staticmethod
    async def get_document(document_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("""
                        SELECT id, division_id, original_filename, storage_path, file_type, status, is_active
                        FROM documents 
                        WHERE id = :document_id
                    """),
                    {"document_id": document_id}
                )
                row = result.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "division_id": row[1],
                        "original_filename": row[2],
                        "storage_path": row[3],
                        "file_type": row[4],
                        "status": row[5],
                        "is_active": row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    @staticmethod
    async def get_documents_by_division(division_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get all active documents in a division."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("""
                        SELECT id, division_id, original_filename, storage_path, file_type, status, is_active
                        FROM documents 
                        WHERE division_id = :division_id AND is_active = true
                        ORDER BY original_filename
                    """),
                    {"division_id": division_id}
                )
                rows = result.fetchall()
                documents = []
                for row in rows:
                    documents.append({
                        "id": row[0],
                        "division_id": row[1],
                        "original_filename": row[2],
                        "storage_path": row[3],
                        "file_type": row[4],
                        "status": row[5],
                        "is_active": row[6]
                    })
                return documents
        except Exception as e:
            logger.error(f"Error getting documents by division: {e}")
            return []
    
# PostgreSQL embedding storage removed - using ChromaDB exclusively
    
    @staticmethod
    async def store_embeddings(embeddings_data: List[Dict[str, Any]]) -> bool:
        """Store multiple embeddings in OpenSearch."""
        # Convert dicts to EmbeddingData model and store via OpenSearch
        try:
            from .models import EmbeddingData as EmbModel
            from .services.opensearch import opensearch_service
            payload = []
            for e in embeddings_data:
                payload.append(
                    EmbModel(
                        document_id=e["document_id"],
                        chunk_text=e["chunk_text"],
                        embedding=e["embedding"],
                        chunk_index=e["chunk_index"],
                        division_id=e.get("division_id"),
                        filename=e.get("filename"),
                        is_active=e.get("is_active"),
                    )
                )
            return await opensearch_service.store_document(payload)
        except Exception as e:
            logger.error(f"Error storing embeddings in OpenSearch: {e}")
            return False
    
    @staticmethod
    async def search_similar_embeddings(
        query_embedding: List[float], 
        division_id: uuid.UUID, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings using OpenSearch vector kNN."""
        try:
            from .services.opensearch import opensearch_service
            os_results = await opensearch_service.search_similar_vector(
                query_embedding=query_embedding,
                division_id=division_id,
                top_k=limit,
            )
            results: List[Dict[str, Any]] = []
            for r in os_results:
                results.append({
                    "chunk_text": r.chunk_text,
                    "chunk_index": r.chunk_index,
                    "filename": r.filename,
                    # Convert similarity score to distance-like metric used elsewhere
                    "distance": 1.0 / (1.0 + float(r.score)),
                })
            return results
        except Exception as e:
            logger.error(f"Error searching similar embeddings in OpenSearch: {e}")
            return []
    
    @staticmethod
    async def log_user_query(
        division_id: Optional[uuid.UUID],
        query_text: str,
        response_text: str,
        user_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Log user query and response."""
        try:
            async with AsyncSessionLocal() as session:
                user_query = UserQuery(
                    division_id=division_id,
                    query_text=query_text,
                    response_text=response_text,
                    user_id=user_id
                )
                session.add(user_query)
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging user query: {e}")
            return False
    
    # Vector Database Management Methods
    
    @staticmethod
    async def delete_document_embeddings(document_id: uuid.UUID) -> bool:
        """Delete all embeddings for a specific document from OpenSearch."""
        from .services.opensearch import opensearch_service
        return await opensearch_service.delete_document(document_id)
    
    @staticmethod
    async def delete_division_embeddings(division_id: uuid.UUID) -> bool:
        """Delete all embeddings for a specific division from OpenSearch (by deleting by query)."""
        try:
            from .services.opensearch import opensearch_service
            # Use OpenSearch delete_by_query for division
            response = opensearch_service.client.delete_by_query(
                index=opensearch_service.index_name,
                body={
                    "query": {"term": {"division_id": str(division_id)}}
                }
            )
            logger.info(f"OpenSearch deleted division embeddings: {response}")
            return True
        except Exception as e:
            logger.error(f"Error deleting division embeddings in OpenSearch: {e}")
            return False
    
    @staticmethod
    async def cleanup_all_embeddings() -> bool:
        """Delete all embeddings from OpenSearch collection (recreate index)."""
        try:
            from .services.opensearch import opensearch_service
            client = opensearch_service.client
            index = opensearch_service.index_name
            if client.indices.exists(index=index):
                client.indices.delete(index=index, ignore=[400, 404])
            # Recreate via service init logic
            opensearch_service.__init__()
            return True
        except Exception as e:
            logger.error(f"Error cleaning up embeddings in OpenSearch: {e}")
            return False
    
    @staticmethod
    async def get_vector_service_stats() -> Dict[str, Any]:
        """Get statistics from OpenSearch index."""
        try:
            from .services.opensearch import opensearch_service
            client = opensearch_service.client
            stats = client.indices.stats(index=opensearch_service.index_name)
            count = client.count(index=opensearch_service.index_name).get("count", 0)
            return {"service": "OpenSearch", "index": opensearch_service.index_name, "doc_count": count, "stats": stats}
        except Exception as e:
            logger.error(f"Failed to get OpenSearch stats: {e}")
            return {"service": "OpenSearch", "status": "error", "error": str(e)}
    
    @staticmethod
    async def update_document_active_status_in_vectors(document_id: uuid.UUID, is_active: bool) -> bool:
        """Update document active status in OpenSearch when it changes in PostgreSQL."""
        from .services.opensearch import opensearch_service
        return await opensearch_service.update_document_active_status(document_id, is_active)


# Initialize database connection
async def init_db():
    """Initialize database connection."""
    try:
        async with async_engine.begin() as conn:
            # Simple connection test
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# Database manager instance
db_manager = DatabaseManager()
