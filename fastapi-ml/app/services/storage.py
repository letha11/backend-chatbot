"""
Object storage service for MinIO integration.
"""
import io
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
from loguru import logger

from ..config import settings


class StorageService:
    """MinIO storage service for document management."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    async def download_file(self, storage_path: str) -> Optional[bytes]:
        """
        Download a file from MinIO storage.
        
        Args:
            storage_path: Path to the file in storage
            
        Returns:
            File content as bytes, or None if error
        """
        try:
            response = self.client.get_object(self.bucket_name, storage_path)
            content = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Successfully downloaded file: {storage_path}")
            return content
        except S3Error as e:
            logger.error(f"Error downloading file {storage_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading file {storage_path}: {e}")
            return None
    
    async def download_file_stream(self, storage_path: str) -> Optional[BinaryIO]:
        """
        Download a file from MinIO storage as a stream.
        
        Args:
            storage_path: Path to the file in storage
            
        Returns:
            File stream, or None if error
        """
        try:
            response = self.client.get_object(self.bucket_name, storage_path)
            # Convert to BytesIO for easier handling
            content = response.read()
            response.close()
            response.release_conn()
            
            stream = io.BytesIO(content)
            logger.info(f"Successfully downloaded file stream: {storage_path}")
            return stream
        except S3Error as e:
            logger.error(f"Error downloading file stream {storage_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading file stream {storage_path}: {e}")
            return None
    
    async def upload_file(
        self, 
        storage_path: str, 
        file_content: bytes, 
        content_type: str = "application/octet-stream"
    ) -> bool:
        """
        Upload a file to MinIO storage.
        
        Args:
            storage_path: Path where to store the file
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_stream = io.BytesIO(file_content)
            self.client.put_object(
                self.bucket_name,
                storage_path,
                file_stream,
                length=len(file_content),
                content_type=content_type
            )
            logger.info(f"Successfully uploaded file: {storage_path}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading file {storage_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading file {storage_path}: {e}")
            return False
    
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from MinIO storage.
        
        Args:
            storage_path: Path to the file in storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.remove_object(self.bucket_name, storage_path)
            logger.info(f"Successfully deleted file: {storage_path}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file {storage_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file {storage_path}: {e}")
            return False
    
    async def file_exists(self, storage_path: str) -> bool:
        """
        Check if a file exists in MinIO storage.
        
        Args:
            storage_path: Path to the file in storage
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, storage_path)
            return True
        except S3Error:
            return False
        except Exception as e:
            logger.error(f"Error checking file existence {storage_path}: {e}")
            return False


# Global storage service instance
storage_service = StorageService()
