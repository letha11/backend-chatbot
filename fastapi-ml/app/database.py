"""
Database connection and models for the FastAPI ML microservice.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text, Column, String, Boolean, DateTime, Integer, Text
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


# Embedding table removed - using ChromaDB exclusively for vector storage


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
    
# PostgreSQL embedding storage removed - using ChromaDB exclusively
    
    @staticmethod
    async def store_embeddings(embeddings_data: List[Dict[str, Any]]) -> bool:
        """Store multiple embeddings in ChromaDB."""
        from .services.vector_manager import vector_manager
        return await vector_manager.store_embeddings(embeddings_data)
    
    @staticmethod
    async def search_similar_embeddings(
        query_embedding: List[float], 
        division_id: uuid.UUID, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings using the configured vector service."""
        from .services.vector_manager import vector_manager
        return await vector_manager.search_similar_embeddings(query_embedding, division_id, limit)
    
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
        """Delete all embeddings for a specific document."""
        from .services.vector_manager import vector_manager
        return await vector_manager.delete_document_embeddings(document_id)
    
    @staticmethod
    async def delete_division_embeddings(division_id: uuid.UUID) -> bool:
        """Delete all embeddings for a specific division."""
        from .services.vector_manager import vector_manager
        return await vector_manager.delete_division_embeddings(division_id)
    
    @staticmethod
    async def cleanup_all_embeddings() -> bool:
        """Delete all embeddings from the vector database."""
        from .services.vector_manager import vector_manager
        return await vector_manager.cleanup_all_embeddings()
    
    @staticmethod
    async def get_vector_service_stats() -> Dict[str, Any]:
        """Get statistics from the vector service."""
        from .services.vector_manager import vector_manager
        return await vector_manager.get_vector_service_stats()
    
    @staticmethod
    async def update_document_active_status_in_vectors(document_id: uuid.UUID, is_active: bool) -> bool:
        """Update document active status in ChromaDB when it changes in PostgreSQL."""
        from .services.vector_manager import vector_manager
        return await vector_manager.update_document_active_status(document_id, is_active)


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
