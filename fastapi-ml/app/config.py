"""
Configuration settings for the FastAPI ML microservice.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/chatbot_control_panel"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "chatbot_control_panel"
    database_user: str = "postgres"
    database_password: str = "password"
    
    # MinIO Object Storage Configuration
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "documents"
    minio_secure: bool = False
    
    # LLM API Configuration
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    use_openrouter: bool = False
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"  # SentenceTransformers model - local and free
    embedding_dimension: int = 384  # SentenceTransformers dimension
    use_openai_embeddings: bool = False  # Use local SentenceTransformers
    
    # LLM Configuration
    llm_model: str = "openai/gpt-oss-120b"  # OpenRouter model format
    max_tokens: int = 1500
    temperature: float = 0.7
    
    # Text Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Vector Search Configuration
    top_k_results: int = 5
    
    # ChromaDB Configuration (Vector Database)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "chatbot_embeddings"
    chroma_persist_directory: Optional[str] = "./chroma_data"
    chroma_use_persistent: bool = True
    
    # Express.js Backend Configuration
    express_api_url: str = "http://localhost:3000"
    internal_api_key: Optional[str] = None
    conversation_history_limit: int = 6
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
