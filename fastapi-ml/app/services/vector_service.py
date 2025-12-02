"""
Vector database service abstraction (deprecated). Using OpenSearch directly.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from uuid import UUID
import asyncio
from loguru import logger

from ..models import SimilarChunk, EmbeddingData


class VectorServiceConfig:
    """Configuration for vector database services."""
    
    def __init__(
        self,
        service_type: str,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs
    ):
        self.service_type = service_type
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.host = host
        self.port = port
        self.extra_config = kwargs


class VectorService(ABC):
    """Deprecated base class (kept for compatibility)."""
    
    def __init__(self, config: VectorServiceConfig):
        self.config = config
        self.service_name = config.service_type
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the vector database connection."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vector database is healthy and accessible."""
        pass
    
    @abstractmethod
    async def store_embeddings(
        self, 
        embeddings_data: List[EmbeddingData],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Store embeddings in the vector database.
        
        Args:
            embeddings_data: List of embedding data to store
            namespace: Optional namespace for organization
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def search_similar(
        self,
        query_embedding: List[float],
        division_id: UUID,
        top_k: int = 5,
        namespace: Optional[str] = None
    ) -> List[SimilarChunk]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query vector
            division_id: Division to search within
            top_k: Number of results to return
            namespace: Optional namespace to search in
            
        Returns:
            List of similar chunks with metadata
        """
        pass
    
    @abstractmethod
    async def delete_embeddings(
        self,
        document_id: UUID,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Delete embeddings for a specific document.
        
        Args:
            document_id: Document ID to delete embeddings for
            namespace: Optional namespace
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def delete_division_embeddings(
        self,
        division_id: UUID,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Delete all embeddings for a division.
        
        Args:
            division_id: Division ID to delete embeddings for
            namespace: Optional namespace
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def cleanup_all(self) -> bool:
        """
        Delete all embeddings from the vector database.
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Statistics dictionary
        """
        pass
    
    async def close(self) -> None:
        """Close the vector database connection."""
        logger.info(f"Closing {self.service_name} vector service")
        self.is_initialized = False


# PostgreSQL and Chroma services removed - using OpenSearch exclusively
