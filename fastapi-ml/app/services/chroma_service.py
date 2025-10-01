"""
ChromaDB vector database service implementation.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
import asyncio
from loguru import logger

from .vector_service import VectorService, VectorServiceConfig
from ..models import SimilarChunk, EmbeddingData

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available. Install with: pip install chromadb")


class ChromaVectorService(VectorService):
    """ChromaDB vector database implementation."""
    
    def __init__(self, config: VectorServiceConfig):
        super().__init__(config)
        self.service_name = "ChromaDB"
        self.client = None
        self.collection = None
        
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB client not available. Install with: pip install chromadb")
        
        # Configuration
        self.collection_name = config.index_name or "chatbot_embeddings"
        self.host = config.host or "localhost"
        self.port = config.port or 8000
        self.persist_directory = config.extra_config.get("persist_directory")
        self.use_persistent = config.extra_config.get("use_persistent", True)
        
        # ChromaDB settings (handled in initialize method)
    
    async def initialize(self) -> bool:
        """Initialize ChromaDB client and collection."""
        try:
            logger.info(f"Initializing ChromaDB service with collection: {self.collection_name}")
            
            # Initialize ChromaDB client using PersistentClient
            if self.use_persistent and self.persist_directory:
                # Use PersistentClient for local data persistence
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"Using ChromaDB PersistentClient with path: {self.persist_directory}")
            elif self.host and self.port and not self.use_persistent:
                # Use HttpClient for remote ChromaDB server
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"Using ChromaDB HttpClient connecting to: {self.host}:{self.port}")
            else:
                # Fallback to in-memory client (for testing)
                self.client = chromadb.EphemeralClient()
                logger.info("Using ChromaDB EphemeralClient (in-memory)")
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Connected to existing ChromaDB collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Chatbot document embeddings"}
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            
            self.is_initialized = True
            logger.info("ChromaDB service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB service: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check ChromaDB service health."""
        try:
            if not self.client:
                return False
            
            # Use heartbeat as health check
            await asyncio.to_thread(self.client.heartbeat)
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    
    async def store_embeddings(
        self, 
        embeddings_data: List[EmbeddingData],
        namespace: Optional[str] = None
    ) -> bool:
        """Store embeddings in ChromaDB."""
        try:
            if not self.collection:
                logger.error("ChromaDB collection not initialized")
                return False
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            
            for embedding_data in embeddings_data:
                vector_id = f"{embedding_data.document_id}_{embedding_data.chunk_index}"
                ids.append(vector_id)
                embeddings.append(embedding_data.embedding)
                
                metadata = {
                    "document_id": str(embedding_data.document_id),
                    "chunk_index": embedding_data.chunk_index,
                    "namespace": namespace or "default"
                }
                
                # Add division_id and filename if available
                if embedding_data.division_id:
                    metadata["division_id"] = str(embedding_data.division_id)
                if embedding_data.filename:
                    metadata["filename"] = embedding_data.filename
                
                # Add document status and active flag for filtering
                if embedding_data.is_active is not None:
                    metadata["is_active"] = embedding_data.is_active
                if embedding_data.document_status:
                    metadata["document_status"] = embedding_data.document_status
                
                metadatas.append(metadata)
                documents.append(embedding_data.chunk_text)
            
            # Add embeddings to collection
            await asyncio.to_thread(
                self.collection.add,
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
            logger.info(f"Successfully stored {len(embeddings)} embeddings in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embeddings in ChromaDB: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: List[float],
        division_id: UUID,
        top_k: int = 5,
        namespace: Optional[str] = None
    ) -> List[SimilarChunk]:
        """Search for similar embeddings in ChromaDB."""
        try:
            if not self.collection:
                logger.error("ChromaDB collection not initialized")
                return []
            
            # Build where clause for filtering by division_id AND active documents only
            where_clause = {
                "$and": [
                    {"division_id": str(division_id)},
                    {"is_active": True}  # Only include active documents
                ]
            }
            if namespace:
                where_clause["$and"].append({"namespace": namespace})
            
            logger.info(f"Querying ChromaDB with where clause (active docs only): {where_clause}")
            # Query ChromaDB with proper filtering
            query_result = await asyncio.to_thread(
                self.collection.query,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["metadatas", "documents", "distances"]
            )
            
            # Convert results to SimilarChunk objects
            similar_chunks = []
            if query_result['ids'] and len(query_result['ids'][0]) > 0:
                for i in range(len(query_result['ids'][0])):
                    metadata = query_result['metadatas'][0][i]
                    document = query_result['documents'][0][i]
                    distance = query_result['distances'][0][i]
                    
                    chunk = SimilarChunk(
                        chunk_text=document,
                        chunk_index=metadata.get("chunk_index", 0),
                        filename=metadata.get("filename", "unknown"),
                        distance=distance
                    )
                    similar_chunks.append(chunk)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks in ChromaDB")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Failed to search embeddings in ChromaDB: {e}")
            return []
    
    async def delete_embeddings(
        self,
        document_id: UUID,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete embeddings for a specific document."""
        try:
            if not self.collection:
                logger.error("ChromaDB collection not initialized")
                return False
            
            # Build where clause
            where_clause = {"document_id": str(document_id)}
            if namespace:
                where_clause["namespace"] = namespace
            
            # Delete embeddings
            await asyncio.to_thread(
                self.collection.delete,
                where=where_clause
            )
            
            logger.info(f"Deleted embeddings for document {document_id} from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embeddings for document {document_id}: {e}")
            return False
    
    async def delete_division_embeddings(
        self,
        division_id: UUID,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete all embeddings for a division."""
        try:
            if not self.collection:
                logger.error("ChromaDB collection not initialized")
                return False
            
            # Build where clause
            where_clause = {"division_id": str(division_id)}
            if namespace:
                where_clause["namespace"] = namespace
            
            # Delete embeddings
            await asyncio.to_thread(
                self.collection.delete,
                where=where_clause
            )
            
            logger.info(f"Deleted all embeddings for division {division_id} from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embeddings for division {division_id}: {e}")
            return False
    
    async def cleanup_all(self) -> bool:
        """Delete all embeddings from ChromaDB collection."""
        try:
            if not self.collection:
                logger.error("ChromaDB collection not initialized")
                return False
            
            # Delete the entire collection and recreate it
            await asyncio.to_thread(self.client.delete_collection, name=self.collection_name)
            
            # Recreate collection
            self.collection = await asyncio.to_thread(
                self.client.create_collection,
                name=self.collection_name,
                metadata={"description": "Chatbot document embeddings"}
            )
            
            logger.info("Cleaned up all embeddings from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup ChromaDB embeddings: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get ChromaDB collection statistics."""
        try:
            if not self.collection:
                return {"service": "ChromaDB", "status": "not_initialized"}
            
            # Get collection count
            count = await asyncio.to_thread(self.collection.count)
            
            return {
                "service": "ChromaDB",
                "status": "active" if self.is_initialized else "inactive",
                "type": "embedded" if self.use_persistent else "remote",
                "total_vector_count": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Failed to get ChromaDB stats: {e}")
            return {"service": "ChromaDB", "status": "error", "error": str(e)}
