"""
Hybrid retriever service combining vector search and BM25 for improved retrieval.
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from loguru import logger
import numpy as np
from pydantic import config

from app.services.opensearch import opensearch_service

from ..models import OpenSearchResult, SimilarChunk
# from .bm25_retriever import bm25_retriever
from ..database import db_manager

from ..config import settings


class HybridRetriever:
    """Hybrid retriever combining vector search and BM25."""
    
    def __init__(self, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_weight: Weight for vector search results (default: 0.7)
            bm25_weight: Weight for BM25 search results (default: 0.3)
        """
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        
        # Ensure weights sum to 1.0
        total_weight = vector_weight + bm25_weight
        if total_weight != 1.0:
            self.vector_weight = vector_weight / total_weight
            self.bm25_weight = bm25_weight / total_weight
            logger.info(f"Adjusted weights: vector={self.vector_weight:.2f}, bm25={self.bm25_weight:.2f}")
    
    async def search(
        self,
        query: str,
        query_embedding: List[float],
        division_id: UUID,
        top_k: int = 5,
        vector_top_k: Optional[int] = None,
        bm25_top_k: Optional[int] = None
    ) -> List[SimilarChunk]:
        """
        Perform hybrid search combining vector and BM25 retrieval.
        
        Args:
            query: Search query text
            query_embedding: Query embedding vector
            division_id: Division to search in
            top_k: Final number of results to return
            vector_top_k: Number of vector results to retrieve (default: top_k * 2)
            bm25_top_k: Number of BM25 results to retrieve (default: top_k * 2)
            
        Returns:
            List of similar chunks with hybrid scores
        """
        try:
            logger.info(f"Performing hybrid search for division {division_id}")
            
            # Set default retrieval counts
            if vector_top_k is None:
                vector_top_k = max(top_k * 2, 10)
            if bm25_top_k is None:
                bm25_top_k = max(top_k * 2, 10)
            
            # Perform both searches in parallel
            vector_task = self._vector_search(query_embedding, division_id, vector_top_k)
            bm25_task = self._opensearch_search(query, division_id, bm25_top_k)
            
            vector_results, bm25_results = await asyncio.gather(
                vector_task, bm25_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(vector_results, Exception):
                logger.error(f"Vector search failed: {vector_results}")
                vector_results = []
            if isinstance(bm25_results, Exception):
                logger.error(f"OPENSEARCH search failed: {bm25_results}")
                bm25_results = []
            
            # Combine and rank results
            hybrid_results = self._combine_results(
                vector_results, bm25_results, top_k
            )
            
            logger.info(f"Hybrid search returned {len(hybrid_results)} results")
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        division_id: UUID,
        top_k: int
    ) -> List[SimilarChunk]:
        """Perform vector search."""
        try:
            # Perform vector kNN search via OpenSearch
            os_results = await opensearch_service.search_similar_vector(
                query_embedding=query_embedding,
                division_id=division_id,
                top_k=top_k
            )

            # Convert OpenSearch results to SimilarChunk using score -> distance (cosine)
            vector_chunks: List[SimilarChunk] = []
            for res in os_results:
                # Convert similarity score (higher is better) to distance-like value
                # Use 1/(1+score) to keep previous contract where lower is better
                distance = 1.0 / (1.0 + float(res.score))
                vector_chunks.append(
                    SimilarChunk(
                        chunk_text=res.chunk_text,
                        chunk_index=res.chunk_index,
                        filename=res.filename,
                        distance=distance,
                    )
                )

            return vector_chunks
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    async def _opensearch_search(
        self,
        query: str,
        division_id: UUID,
        top_k: int
    ) -> List[OpenSearchResult]:
        """Perform BM25 search."""
        try:
            return await opensearch_service.search_similar(query, division_id, top_k)
            
        except Exception as e:
            logger.error(f"Error in OPENSEARCH search: {e}")
            return []
    
    def _combine_results(
        self,
        vector_results: List[SimilarChunk],
        bm25_results: List[OpenSearchResult],
        top_k: int
    ) -> List[SimilarChunk]:
        """
        Combine vector and BM25 results using weighted scoring.
        
        Args:
            vector_results: Results from vector search
            bm25_results: Results from OPENSEARCH search
            top_k: Number of final results to return
            
        Returns:
            Combined and ranked results
        """
        try:
            # Create a mapping of chunk identifiers to results
            chunk_map: Dict[str, Dict[str, Any]] = {}
            
            # Add vector results
            for i, chunk in enumerate(vector_results):
                chunk_id = self._get_chunk_id(chunk)
                vector_score = 1.0 / (1.0 + chunk.distance)  # Convert distance to similarity score
                
                chunk_map[chunk_id] = {
                    'chunk': chunk,
                    'vector_score': vector_score,
                    'vector_rank': i + 1,
                    'bm25_score': 0.0,
                    'bm25_rank': float('inf')
                }
            
            # Add BM25 results
            for i, result in enumerate(bm25_results):
                chunk_id = self._get_opensearch_chunk_id(result)
                # OpenSearch score is higher for better matches, use it directly as similarity score
                bm25_score = result.score

                if chunk_id in chunk_map:
                    # Update existing entry
                    chunk_map[chunk_id]['bm25_score'] = bm25_score
                    chunk_map[chunk_id]['bm25_rank'] = i + 1
                else:
                    # Convert OpenSearchResult to SimilarChunk for consistency
                    similar_chunk = SimilarChunk(
                        chunk_text=result.chunk_text,
                        chunk_index=result.chunk_index,
                        filename=result.filename,
                        distance=1.0 / (1.0 + bm25_score)  # Convert score to distance format
                    )
                    
                    # Add new entry
                    chunk_map[chunk_id] = {
                        'chunk': similar_chunk,
                        'vector_score': 0.0,
                        'vector_rank': float('inf'),
                        'bm25_score': bm25_score,
                        'bm25_rank': i + 1
                    }

            # Calculate hybrid scores
            hybrid_results = []
            for chunk_id, data in chunk_map.items():
                # Normalize scores using rank-based normalization
                vector_norm_score = self._normalize_rank_score(
                    data['vector_rank'], len(vector_results)
                )
                bm25_norm_score = self._normalize_rank_score(
                    data['bm25_rank'], len(bm25_results)
                )

                # Calculate hybrid score
                hybrid_score = (
                    self.vector_weight * vector_norm_score +
                    self.bm25_weight * bm25_norm_score
                )

                if hybrid_score < settings.result_threshold:
                    logger.info(f"Skipping chunk {chunk_id} with hybrid score {hybrid_score}")
                    continue
                
                # Create new chunk with hybrid distance
                hybrid_chunk = SimilarChunk(
                    chunk_text=data['chunk'].chunk_text,
                    chunk_index=data['chunk'].chunk_index,
                    filename=data['chunk'].filename,
                    distance=1.0 / (1.0 + hybrid_score)  # Convert back to distance
                )
                
                # Detailed logging of per-chunk scores
                logger.info(
                    f"Hybrid scoring | id={chunk_id} | vector_score={data['vector_score']:.4f} (rank={data['vector_rank']}) | "
                    f"bm25_score={data['bm25_score']:.4f} (rank={data['bm25_rank']}) | combined={hybrid_score:.4f}"
                )

                hybrid_results.append((hybrid_score, hybrid_chunk))
            
            # Sort by hybrid score (descending) and return top_k
            hybrid_results.sort(key=lambda x: x[0], reverse=True)

            print(f"Hybrid results: {hybrid_results}")
            final_results = [chunk for _, chunk in hybrid_results[:top_k]]
            # threshold = 0.5
            # filtered_results = [chunk for _, chunk in hybrid_results if chunk.distance > threshold]
            # final_results = filtered_results[:top_k]
            
            logger.info(f"Combined {len(vector_results)} vector and {len(bm25_results)} BM25 results into {len(final_results)} hybrid results")
            return final_results
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            return []
    
    def _get_chunk_id(self, chunk: SimilarChunk) -> str:
        """Generate a unique identifier for a chunk."""
        return f"{chunk.filename}_{chunk.chunk_index}"

    def _get_opensearch_chunk_id(self, result: OpenSearchResult) -> str:
        """Generate a unique identifier for a chunk."""
        return f"{result.document_id}_{result.chunk_index}"
    
    def _normalize_rank_score(self, rank: float, total_results: int) -> float:
        """
        Normalize rank to a score between 0 and 1.
        
        Args:
            rank: Rank of the result (1-based, or inf if not found)
            total_results: Total number of results
            
        Returns:
            Normalized score between 0 and 1
        """
        if rank == float('inf') or total_results == 0:
            return 0.0
        
        # Use reciprocal rank normalization
        return 1.0 / rank
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hybrid retriever statistics."""
        try:
            # bm25_stats = bm25_retriever.get_stats()
            
            return {
                "service": "HybridRetriever",
                "vector_weight": self.vector_weight,
                # "bm25_weight": self.bm25_weight,
                # "bm25_retriever": bm25_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting hybrid retriever stats: {e}")
            return {"service": "HybridRetriever", "status": "error", "error": str(e)}


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
