"""
Vector service factory placeholder. ChromaDB removed in favor of OpenSearch-only.
"""

from typing import Optional


class VectorServiceFactory:
    """Placeholder factory (no-op since OpenSearch is used directly)."""
    _instance: Optional[None] = None

    @classmethod
    async def get_vector_service(cls, force_recreate: bool = False):  # type: ignore
        return None

    @classmethod
    async def health_check(cls) -> bool:
        return True

    @classmethod
    async def cleanup_service(cls) -> bool:
        return True

    @classmethod
    async def get_stats(cls) -> dict:
        return {"service": "OpenSearch"}


# Global instance
vector_service_factory = VectorServiceFactory()
