"""
Vector database management API routes.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from ..database import db_manager
from ..services.opensearch import opensearch_service

router = APIRouter(prefix="/vector", tags=["vector"])


# Vector service switching removed - using ChromaDB exclusively
class VectorServiceResponse(BaseModel):
    """Response model for vector service operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/health", response_model=VectorServiceResponse)
async def get_vector_health() -> VectorServiceResponse:
    """Get health/status of OpenSearch index."""
    try:
        # Basic check by fetching stats
        stats = await db_manager.get_vector_service_stats()
        health = True if stats else False
        
        return VectorServiceResponse(
            success=health,
            message="OpenSearch health check completed",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting OpenSearch health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=VectorServiceResponse)
async def get_vector_stats() -> VectorServiceResponse:
    """Get OpenSearch index statistics."""
    try:
        stats = await db_manager.get_vector_service_stats()
        
        return VectorServiceResponse(
            success=True,
            message="OpenSearch statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting OpenSearch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vector service switching removed - using ChromaDB exclusively


@router.post("/cleanup", response_model=VectorServiceResponse)
async def cleanup_vector_data() -> VectorServiceResponse:
    """Clean up all vector data from OpenSearch (recreate index)."""
    try:
        success = await db_manager.cleanup_all_embeddings()
        
        if success:
            return VectorServiceResponse(
                success=True,
                message="Successfully cleaned up OpenSearch vector data"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to cleanup OpenSearch data"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up OpenSearch data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{document_id}", response_model=VectorServiceResponse)
async def delete_document_vectors(document_id: str) -> VectorServiceResponse:
    """Delete all vectors for a specific document from OpenSearch."""
    try:
        from uuid import UUID
        doc_uuid = UUID(document_id)
        
        success = await db_manager.delete_document_embeddings(doc_uuid)
        
        if success:
            return VectorServiceResponse(
                success=True,
                message=f"Successfully deleted vectors for document {document_id} from OpenSearch"
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
    """Delete all vectors for a specific division from OpenSearch."""
    try:
        from uuid import UUID
        div_uuid = UUID(division_id)
        
        success = await db_manager.delete_division_embeddings(div_uuid)
        
        if success:
            return VectorServiceResponse(
                success=True,
                message=f"Successfully deleted vectors for division {division_id} from OpenSearch"
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
    """Update the active status of a document in OpenSearch."""
    try:
        from uuid import UUID
        document_uuid = UUID(document_id)
        
        success = await db_manager.update_document_active_status_in_vectors(document_uuid, is_active)
        
        if success:
            status_text = "activated" if is_active else "deactivated"
            return VectorServiceResponse(
                success=True,
                message=f"Successfully {status_text} document {document_id} in OpenSearch",
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