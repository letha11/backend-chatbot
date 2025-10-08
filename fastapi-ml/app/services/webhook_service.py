"""
Webhook service for sending notifications to Express.js backend.
"""
import httpx
from typing import Dict, Any, Optional
from loguru import logger
from ..config import settings


class WebhookService:
    """Service for sending webhook notifications to Express.js backend."""
    
    def __init__(self):
        self.express_api_url = settings.express_api_url
        self.internal_api_key = settings.internal_api_key
    
    async def send_document_processing_notification(
        self,
        document_id: str,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send document processing notification to Express.js backend.
        
        Args:
            document_id: UUID of the document
            status: Processing status (parsing, parsed, embedding, embedded, failed)
            message: Human-readable message
            metadata: Additional metadata to include
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            webhook_url = f"{self.express_api_url}/api/v1/events/webhook/document-processing"
            
            payload = {
                "documentId": document_id,
                "status": status,
                "message": message,
                "metadata": metadata or {}
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Key": self.internal_api_key or "default-key"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook notification sent successfully: {document_id} - {status}")
                    return True
                else:
                    logger.error(f"Webhook notification failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False
    
    async def notify_parsing_started(self, document_id: str, filename: str, file_type: str) -> bool:
        """Notify that document parsing has started."""
        return await self.send_document_processing_notification(
            document_id=document_id,
            status="parsing",
            message=f"Started parsing document: {filename}",
            metadata={
                "filename": filename,
                "fileType": file_type,
                "stage": "parsing"
            }
        )
    
    async def notify_parsing_completed(self, document_id: str, filename: str, chunk_count: int) -> bool:
        """Notify that document parsing has completed."""
        return await self.send_document_processing_notification(
            document_id=document_id,
            status="parsed",
            message=f"Successfully parsed document: {filename} into {chunk_count} chunks",
            metadata={
                "filename": filename,
                "chunkCount": chunk_count,
                "stage": "parsing_complete"
            }
        )
    
    async def notify_embedding_started(self, document_id: str, filename: str) -> bool:
        """Notify that embedding generation has started."""
        return await self.send_document_processing_notification(
            document_id=document_id,
            status="embedding",
            message=f"Started generating embeddings for: {filename}",
            metadata={
                "filename": filename,
                "stage": "embedding"
            }
        )
    
    async def notify_embedding_completed(self, document_id: str, filename: str, embedding_count: int) -> bool:
        """Notify that embedding generation has completed."""
        return await self.send_document_processing_notification(
            document_id=document_id,
            status="embedded",
            message=f"Successfully generated {embedding_count} embeddings for: {filename}",
            metadata={
                "filename": filename,
                "embeddingCount": embedding_count,
                "stage": "embedding_complete"
            }
        )
    
    async def notify_processing_failed(self, document_id: str, filename: str, error: str, stage: str) -> bool:
        """Notify that document processing has failed."""
        return await self.send_document_processing_notification(
            document_id=document_id,
            status="failed",
            message=f"Failed to process document: {filename} at stage: {stage}",
            metadata={
                "filename": filename,
                "error": error,
                "stage": stage,
                "failed": True
            }
        )


# Global webhook service instance
webhook_service = WebhookService()
