"""
ChromaDB vector database management service.
Handles all vector operations using ChromaDB exclusively.
"""
from typing import List, Dict, Any
from uuid import UUID
from loguru import logger

from ..models import EmbeddingData


class VectorManager:
    """Manages ChromaDB vector database operations."""
    
    @staticmethod
    async def store_embeddings(embeddings_data: List[Dict[str, Any]]) -> bool:
        """Store multiple embeddings in ChromaDB."""
        from .vector_factory import vector_service_factory
        from ..database import AsyncSessionLocal, text
        
        try:
            # Get the ChromaDB service
            vector_service = await vector_service_factory.get_vector_service()
            
            # Convert dict data to EmbeddingData objects with metadata
            embedding_objects = []
            
            # Get document metadata for all embeddings (including is_active status)
            async with AsyncSessionLocal() as session:
                for embedding_data in embeddings_data:
                    # Get document metadata including active status
                    result = await session.execute(
                        text("""
                            SELECT division_id, original_filename, is_active, status
                            FROM documents 
                            WHERE id = :document_id
                        """),
                        {"document_id": embedding_data["document_id"]}
                    )
                    row = result.fetchone()
                    
                    if row:
                        division_id, filename, is_active, status = row
                        # Create embedding object with complete metadata
                        embedding_obj = EmbeddingData(
                            document_id=embedding_data["document_id"],
                            chunk_text=embedding_data["chunk_text"],
                            embedding=embedding_data["embedding"],
                            chunk_index=embedding_data["chunk_index"],
                            division_id=division_id,
                            filename=filename,
                            is_active=is_active,
                            document_status=status
                        )
                        embedding_objects.append(embedding_obj)
                    else:
                        logger.warning(f"Document {embedding_data['document_id']} not found in database")
                        # Create embedding without metadata (fallback)
                        embedding_obj = EmbeddingData(
                            document_id=embedding_data["document_id"],
                            chunk_text=embedding_data["chunk_text"],
                            embedding=embedding_data["embedding"],
                            chunk_index=embedding_data["chunk_index"]
                        )
                        embedding_objects.append(embedding_obj)
            
            # Store in ChromaDB
            success = await vector_service.store_embeddings(embedding_objects)
            
            if success:
                logger.info(f"Successfully stored {len(embedding_objects)} embeddings in ChromaDB")
            else:
                logger.error("Failed to store embeddings in ChromaDB")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing embeddings in ChromaDB: {e}")
            return False
    
    @staticmethod
    async def search_similar_embeddings(
        query_embedding: List[float], 
        division_id: UUID, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings in ChromaDB."""
        from .vector_factory import vector_service_factory
        
        try:
            # Get the ChromaDB service
            vector_service = await vector_service_factory.get_vector_service()
            
            # Search using ChromaDB
            similar_chunks = await vector_service.search_similar(
                query_embedding, division_id, limit
            )
            
            # Convert SimilarChunk objects to dict format for backward compatibility
            results = []
            for chunk in similar_chunks:
                results.append({
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "filename": chunk.filename,
                    "distance": chunk.distance
                })
            
            logger.info(f"Found {len(results)} similar chunks in ChromaDB for division {division_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar embeddings in ChromaDB: {e}")
            return []
    
    @staticmethod
    async def delete_document_embeddings(document_id: UUID) -> bool:
        """Delete all embeddings for a specific document from ChromaDB."""
        from .vector_factory import vector_service_factory
        
        try:
            vector_service = await vector_service_factory.get_vector_service()
            
            # Delete from ChromaDB
            success = await vector_service.delete_embeddings(document_id)
            
            if success:
                logger.info(f"Successfully deleted embeddings for document {document_id} from ChromaDB")
            else:
                logger.error(f"Failed to delete embeddings for document {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document embeddings from ChromaDB: {e}")
            return False
    
    @staticmethod
    async def delete_division_embeddings(division_id: UUID) -> bool:
        """Delete all embeddings for a specific division from ChromaDB."""
        from .vector_factory import vector_service_factory
        
        try:
            vector_service = await vector_service_factory.get_vector_service()
            
            # Delete from ChromaDB
            success = await vector_service.delete_division_embeddings(division_id)
            
            if success:
                logger.info(f"Successfully deleted embeddings for division {division_id} from ChromaDB")
            else:
                logger.error(f"Failed to delete embeddings for division {division_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting division embeddings from ChromaDB: {e}")
            return False
    
    @staticmethod
    async def cleanup_all_embeddings() -> bool:
        """Delete all embeddings from ChromaDB."""
        from .vector_factory import vector_service_factory
        
        try:
            vector_service = await vector_service_factory.get_vector_service()
            
            # Cleanup ChromaDB
            success = await vector_service.cleanup_all()
            
            if success:
                logger.info("Successfully cleaned up all embeddings from ChromaDB")
            else:
                logger.error("Failed to cleanup embeddings from ChromaDB")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cleaning up embeddings from ChromaDB: {e}")
            return False
    
    @staticmethod
    async def get_vector_service_stats() -> Dict[str, Any]:
        """Get statistics from ChromaDB service."""
        from .vector_factory import vector_service_factory
        
        try:
            vector_service = await vector_service_factory.get_vector_service()
            stats = await vector_service.get_stats()
            logger.info(f"ChromaDB stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting ChromaDB stats: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def update_document_active_status(document_id: UUID, is_active: bool) -> bool:
        """Update the is_active status for all embeddings of a document in ChromaDB."""
        from .vector_factory import vector_service_factory
        from ..database import AsyncSessionLocal, text
        
        try:
            vector_service = await vector_service_factory.get_vector_service()
            
            # Get current document metadata
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("""
                        SELECT division_id, original_filename, status
                        FROM documents 
                        WHERE id = :document_id
                    """),
                    {"document_id": document_id}
                )
                row = result.fetchone()
                
                if not row:
                    logger.warning(f"Document {document_id} not found in database")
                    return False
                
                division_id, filename, status = row
            
            # Get all embeddings for this document from ChromaDB
            collection = vector_service.collection
            if not collection:
                logger.error("ChromaDB collection not initialized")
                return False
            
            # Query for all embeddings of this document
            results = collection.get(
                where={"document_id": str(document_id)},
                include=["metadatas", "documents", "embeddings"]
            )
            
            if not results['ids']:
                logger.info(f"No embeddings found for document {document_id}")
                return True
            
            # Update metadata for all chunks of this document
            updated_metadatas = []
            for metadata in results['metadatas']:
                metadata['is_active'] = is_active
                metadata['document_status'] = status
                updated_metadatas.append(metadata)
            
            # Update the embeddings with new metadata
            collection.update(
                ids=results['ids'],
                metadatas=updated_metadatas
            )
            
            logger.info(f"Updated {len(results['ids'])} embeddings for document {document_id} - is_active: {is_active}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document active status in ChromaDB: {e}")
            return False


# Global instance
vector_manager = VectorManager()
