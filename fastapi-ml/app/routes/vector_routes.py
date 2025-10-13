"""
Vector database management API routes.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from ..services.vector_factory import vector_service_factory
from ..database import db_manager

router = APIRouter(prefix="/vector", tags=["vector"])


# Vector service switching removed - using ChromaDB exclusively
class VectorServiceResponse(BaseModel):
    """Response model for vector service operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/health", response_model=VectorServiceResponse)
async def get_vector_health() -> VectorServiceResponse:
    """Get health status of ChromaDB service."""
    try:
        # Get ChromaDB health status
        health = await vector_service_factory.health_check()
        
        # Get ChromaDB stats
        stats = await vector_service_factory.get_stats()
        
        return VectorServiceResponse(
            success=health,
            message="ChromaDB health check completed",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting ChromaDB health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=VectorServiceResponse)
async def get_vector_stats() -> VectorServiceResponse:
    """Get ChromaDB statistics."""
    try:
        stats = await vector_service_factory.get_stats()
        
        return VectorServiceResponse(
            success=True,
            message="ChromaDB statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting ChromaDB stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vector service switching removed - using ChromaDB exclusively


@router.post("/cleanup", response_model=VectorServiceResponse)
async def cleanup_vector_data() -> VectorServiceResponse:
    """Clean up all vector data from ChromaDB."""
    try:
        success = await vector_service_factory.cleanup_service()
        
        if success:
            return VectorServiceResponse(
                success=True,
                message="Successfully cleaned up ChromaDB vector data"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to cleanup ChromaDB data"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up ChromaDB data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{document_id}", response_model=VectorServiceResponse)
async def delete_document_vectors(document_id: str) -> VectorServiceResponse:
    """Delete all vectors for a specific document."""
    try:
        from uuid import UUID
        doc_uuid = UUID(document_id)
        
        success = await db_manager.delete_document_embeddings(doc_uuid)
        
        if success:
            return VectorServiceResponse(
                success=True,
                message=f"Successfully deleted vectors for document {document_id}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document vectors"
            )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/division/{division_id}", response_model=VectorServiceResponse)
async def delete_division_vectors(division_id: str) -> VectorServiceResponse:
    """Delete all vectors for a specific division."""
    try:
        from uuid import UUID
        div_uuid = UUID(division_id)
        
        success = await db_manager.delete_division_embeddings(div_uuid)
        
        if success:
            return VectorServiceResponse(
                success=True,
                message=f"Successfully deleted vectors for division {division_id}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete division vectors"
            )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid division ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting division vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/document/{document_id}/active", response_model=VectorServiceResponse)
async def update_document_active_status(
    document_id: str,
    is_active: bool = Query(..., description="Set document active status")
) -> VectorServiceResponse:
    """Update the active status of a document in ChromaDB."""
    try:
        from uuid import UUID
        document_uuid = UUID(document_id)
        
        success = await db_manager.update_document_active_status_in_vectors(document_uuid, is_active)
        
        if success:
            status_text = "activated" if is_active else "deactivated"
            return VectorServiceResponse(
                success=True,
                message=f"Successfully {status_text} document {document_id} in ChromaDB",
                data={"document_id": document_id, "is_active": is_active}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update document {document_id} active status"
            )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document active status: {e}")
        raise HTTPException(status_code=500, detail=str(e))