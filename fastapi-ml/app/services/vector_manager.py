"""
Vector database management facade now using OpenSearch for storage and retrieval.
"""
from typing import List, Dict, Any
from uuid import UUID
from loguru import logger

from app.services.opensearch import opensearch_service

from ..models import EmbeddingData


class VectorManager:
    """Manages vector operations backed by OpenSearch."""
    
    @staticmethod
    async def store_embeddings(embeddings_data: List[Dict[str, Any]]) -> bool:
        """Store multiple embeddings in OpenSearch with metadata enrichment from DB."""
        from ..database import AsyncSessionLocal, text
        
        try:
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
            
            # Store in OpenSearch
            success = await opensearch_service.store_document(embedding_objects)
            
            if success:
                logger.info(f"Successfully stored {len(embedding_objects)} embeddings in OpenSearch")
            else:
                logger.error("Failed to store embeddings in OpenSearch")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing embeddings in OpenSearch: {e}")
            return False
    
    @staticmethod
    async def search_similar_embeddings(
        query_embedding: List[float], 
        division_id: UUID, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings in OpenSearch (kNN)."""
        
        try:
            # Search using OpenSearch kNN
            os_results = await opensearch_service.search_similar_vector(
                query_embedding=query_embedding, division_id=division_id, top_k=limit
            )
            
            # Convert SimilarChunk objects to dict format for backward compatibility
            results = []
            for hit in os_results:
                distance = 1.0 / (1.0 + float(hit.score))
                if distance > 1.2:
                    continue
                results.append({
                    "chunk_text": hit.chunk_text,
                    "chunk_index": hit.chunk_index,
                    "filename": hit.filename,
                    "distance": distance
                })
            
            logger.info(f"Found {len(results)} similar chunks in OpenSearch for division {division_id}")
            logger.info(f"Results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar embeddings in OpenSearch: {e}")
            return []
    
    @staticmethod
    async def delete_document_embeddings(document_id: UUID) -> bool:
        """Delete all embeddings for a specific document from OpenSearch."""
        
        try:
            success = await opensearch_service.delete_document(document_id)
            
            if success:
                logger.info(f"Successfully deleted embeddings for document {document_id} from OpenSearch")
            else:
                logger.error(f"Failed to delete embeddings for document {document_id} in OpenSearch")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document embeddings from OpenSearch: {e}")
            return False
    
    @staticmethod
    async def delete_division_embeddings(division_id: UUID) -> bool:
        """Delete all embeddings for a specific division from OpenSearch."""
        
        try:
            response = opensearch_service.client.delete_by_query(
                index=opensearch_service.index_name,
                body={"query": {"term": {"division_id": str(division_id)}}}
            )
            success = True
            
            if success:
                logger.info(f"Successfully deleted embeddings for division {division_id} from OpenSearch")
            else:
                logger.error(f"Failed to delete embeddings for division {division_id} in OpenSearch")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting division embeddings from OpenSearch: {e}")
            return False
    
    @staticmethod
    async def cleanup_all_embeddings() -> bool:
        """Delete all embeddings from OpenSearch (recreate index)."""
        
        try:
            client = opensearch_service.client
            index = opensearch_service.index_name
            if client.indices.exists(index=index):
                client.indices.delete(index=index, ignore=[400, 404])
            # Recreate index via re-init
            opensearch_service.__init__()
            success = True
            
            if success:
                logger.info("Successfully cleaned up all embeddings from OpenSearch")
            else:
                logger.error("Failed to cleanup embeddings from OpenSearch")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cleaning up embeddings from OpenSearch: {e}")
            return False
    
    @staticmethod
    async def get_vector_service_stats() -> Dict[str, Any]:
        """Get statistics from OpenSearch index."""
        
        try:
            client = opensearch_service.client
            stats = client.indices.stats(index=opensearch_service.index_name)
            count = client.count(index=opensearch_service.index_name).get("count", 0)
            data = {"service": "OpenSearch", "index": opensearch_service.index_name, "doc_count": count, "stats": stats}
            logger.info(f"OpenSearch stats: {data}")
            return data
        except Exception as e:
            logger.error(f"Error getting OpenSearch stats: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def update_document_active_status(document_id: UUID, is_active: bool) -> bool:
        """Update the is_active status for all embeddings of a document in OpenSearch."""
        from ..database import AsyncSessionLocal, text
        
        try:
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
            
            # Update the document active status in OpenSearch
            response = await opensearch_service.update_document_active_status(document_id, is_active)
            if not response:
                logger.error(f"Failed to update document active status in OpenSearch for document {document_id}")
                return False
            
            logger.info(f"Updated {len(results['ids'])} embeddings for document {document_id} - is_active: {is_active}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document active status in OpenSearch: {e}")
            return False


# Global instance
vector_manager = VectorManager()
