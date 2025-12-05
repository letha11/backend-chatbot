"""
Embedding generation service using SentenceTransformers or OpenAI.
"""
import asyncio
from typing import List, Optional, Union
from uuid import UUID
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from loguru import logger

from ..config import settings
from ..models import EmbeddingData, DocumentChunk


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.use_openai = settings.use_openai_embeddings
        self.embedding_dimension = settings.embedding_dimension
        
        if self.use_openai:
            # Determine which API to use for embeddings
            if settings.use_openrouter and settings.openrouter_api_key:
                # Use OpenRouter for embeddings
                self.openai_client = openai.OpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=settings.openrouter_base_url
                )
                logger.info("Initialized OpenRouter embedding service")
            elif settings.openai_api_key:
                # Use OpenAI directly for embeddings
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("Initialized OpenAI embedding service")
            else:
                raise ValueError("API key is required when use_openai_embeddings=True (either OpenAI or OpenRouter)")
            self.model = None
        else:
            # Initialize SentenceTransformers model
            self.model = SentenceTransformer(settings.embedding_model)
            self.openai_client = None
            logger.info(f"Initialized SentenceTransformers with model: {settings.embedding_model}")
    
    async def generate_embeddings(
        self, 
        chunks: List[DocumentChunk], 
        document_id: str,
        filename: str,
        division_id: UUID,
        is_active: bool
    ) -> List[EmbeddingData]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: List of document chunks
            document_id: UUID of the document
            filename: Original filename of the document
            division_id: UUID of the division
            is_active: Whether the document is active
        Returns:
            List of EmbeddingData objects
        """
        if not chunks:
            logger.warning("No chunks provided for embedding generation")
            return []
        
        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            
            # Extract text from chunks
            texts = [chunk.text for chunk in chunks]
            
            # Generate embeddings
            # if self.use_openai:
            #     embeddings = await self._generate_openai_embeddings(texts)
            # else:
            embeddings = await self._generate_sentence_transformer_embeddings(texts)
            
            if embeddings is None:
                logger.error("Failed to generate embeddings")
                return []
            
            # Create EmbeddingData objects
            embedding_data_list = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                embedding_data = EmbeddingData(
                    document_id=document_id,
                    chunk_text=chunk.text,
                    embedding=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                    chunk_index=chunk.index,
                    is_active=is_active,
                    filename=filename,
                    division_id=division_id,
                )
                embedding_data_list.append(embedding_data)
            
            logger.info(f"Successfully generated {len(embedding_data_list)} embeddings")
            return embedding_data_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for a query string.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector as list of floats, or None if error
        """
        try:
            # if self.use_openai:
            #     embeddings = await self._generate_openai_embeddings([query])
            #     if embeddings:
            #         return embeddings[0].tolist() if isinstance(embeddings[0], np.ndarray) else embeddings[0]
            # else:
            embeddings = await self._generate_sentence_transformer_embeddings([query])
            if embeddings:
                return embeddings[0].tolist() if isinstance(embeddings[0], np.ndarray) else embeddings[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return None
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings using OpenAI API."""
        try:
            logger.info(f"Generating OpenAI embeddings for {len(texts)} texts")
            
            # OpenAI has a limit on batch size, so we might need to process in batches
            batch_size = 100  # Conservative batch size
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                response = await asyncio.to_thread(
                    self.openai_client.embeddings.create,
                    model="text-embedding-ada-002",
                    input=batch_texts
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            logger.info(f"Successfully generated {len(all_embeddings)} OpenAI embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            return None
    
    async def _generate_sentence_transformer_embeddings(
        self, 
        texts: List[str]
    ) -> Optional[List[np.ndarray]]:
        """Generate embeddings using SentenceTransformers."""
        try:
            logger.info(f"Generating SentenceTransformer embeddings for {len(texts)} texts")
            
            # Run in thread to avoid blocking
            embeddings = await asyncio.to_thread(
                self.model.encode,
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10  # Show progress for large batches
            )
            
            # Convert to list of arrays
            embedding_list = [embeddings[i] for i in range(len(embeddings))]
            
            logger.info(f"Successfully generated {len(embedding_list)} SentenceTransformer embeddings")
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error generating SentenceTransformer embeddings: {e}")
            return None
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        if self.use_openai:
            return 1536  # OpenAI text-embedding-ada-002 dimension
        else:
            # For SentenceTransformers, we can get the actual dimension
            if hasattr(self.model, 'get_sentence_embedding_dimension'):
                return self.model.get_sentence_embedding_dimension()
            else:
                return self.embedding_dimension  # Fallback to config
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model."""
        if self.use_openai:
            if settings.use_openrouter:
                return {
                    "provider": "OpenRouter",
                    "model": "text-embedding-ada-002",
                    "dimension": 1536,
                    "base_url": settings.openrouter_base_url
                }
            else:
                return {
                    "provider": "OpenAI",
                    "model": "text-embedding-ada-002",
                    "dimension": 1536
                }
        else:
            return {
                "provider": "SentenceTransformers",
                "model": settings.embedding_model,
                "dimension": self.get_embedding_dimension()
            }


# Global embedding service instance
embedding_service = EmbeddingService()
