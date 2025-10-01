"""
Vector service factory for ChromaDB exclusively.
"""
from typing import Optional
from loguru import logger

from .vector_service import VectorService, VectorServiceConfig
from .chroma_service import ChromaVectorService, CHROMADB_AVAILABLE
from ..config import settings


class VectorServiceFactory:
    """Factory for ChromaDB vector database service."""
    
    _instance: Optional[VectorService] = None
    
    @classmethod
    async def get_vector_service(cls, force_recreate: bool = False) -> VectorService:
        """
        Get the ChromaDB vector service instance.
        
        Args:
            force_recreate: Force recreation of the service instance
            
        Returns:
            Initialized ChromaDB service instance
        """
        # Always use ChromaDB - no service type checking needed
        if cls._instance is None or force_recreate:
            if cls._instance:
                await cls._instance.close()
            
            cls._instance = await cls._create_chroma_service()
        
        return cls._instance
    
    @classmethod
    async def _create_chroma_service(cls) -> VectorService:
        """Create a ChromaDB service instance."""
        logger.info("Creating ChromaDB vector service")
        
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("ChromaDB not available. Install with: pip install chromadb>=1.1.0")
        
        config = VectorServiceConfig(
            service_type="chroma",
            index_name=settings.chroma_collection_name,
            host=settings.chroma_host,
            port=settings.chroma_port,
            persist_directory=settings.chroma_persist_directory,
            use_persistent=settings.chroma_use_persistent
        )
        service = ChromaVectorService(config)
        
        # Initialize the service
        if await service.initialize():
            logger.info("Successfully initialized ChromaDB vector service")
            return service
        else:
            raise RuntimeError("Failed to initialize ChromaDB vector service")
    
    @classmethod
    async def health_check(cls) -> bool:
        """Check health of ChromaDB service."""
        try:
            service = await cls.get_vector_service()
            return await service.health_check()
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    
    @classmethod
    async def cleanup_service(cls) -> bool:
        """
        Cleanup ChromaDB vector service data.
        
        Returns:
            Success status
        """
        try:
            service = await cls.get_vector_service()
            return await service.cleanup_all()
        except Exception as e:
            logger.error(f"Failed to cleanup ChromaDB service: {e}")
            return False
    
    @classmethod
    async def get_stats(cls) -> dict:
        """Get ChromaDB service statistics."""
        try:
            service = await cls.get_vector_service()
            return await service.get_stats()
        except Exception as e:
            logger.error(f"Failed to get ChromaDB stats: {e}")
            return {"error": str(e)}


# Global instance
vector_service_factory = VectorServiceFactory()
