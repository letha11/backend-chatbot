from typing import Any, Dict, List
import uuid
from loguru import logger
from app.config import settings
from opensearchpy import OpenSearch

from app.models import EmbeddingData, OpenSearchResult

class OpenSearchService:
    """Service for interacting with OpenSearch."""

    def __init__(self):
        """Initialize the OpenSearch service."""
        logger.info(f"Initializing OpenSearch service with host: {settings.opensearch_host}:{settings.opensearch_port} and username: {settings.opensearch_username}, Password: {settings.opensearch_password}")
        self.client = OpenSearch(
            hosts=[f"{settings.opensearch_host}:{settings.opensearch_port}"],
            http_compress=True,
            http_auth=(settings.opensearch_username, settings.opensearch_password),
            use_ssl=False,
            verify_certs=False,
        )

        self.index_name = "documents"

        is_index_exists = self.client.indices.exists(index=self.index_name)
        if not is_index_exists:
            # Create index with both BM25 (text) and kNN vector support
            self.client.indices.create(
                index=self.index_name,
                body={
                    "settings": {
                        "index": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0,
                            "knn": True
                        }
                    },
                    "mappings": {
                        "properties": {
                            "document_id": {
                                "type": "keyword"
                            },
                            "chunk_index": {
                                "type": "long"
                            },
                            "chunk_text": {
                                "type": "text"
                            },
                            "division_id": {
                                "type": "keyword"
                            },
                            "filename": {
                                "type": "keyword"
                            },
                            "is_active": {
                                "type": "boolean"
                            },
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": settings.embedding_dimension,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "l2",
                                    "engine": "faiss"
                                }
                            }
                        }
                    }

                }
            )

    async def search_similar(
        self,
        query: str,
        division_id: uuid.UUID,
        top_k: int = 5,
    ) -> List[OpenSearchResult]:
        """
        Search for similar active documents in OpenSearch (using BM25).
        """
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "from": 0, "size": top_k,
                    "query": {
                        "bool": {
                            "must": [
                                { "match": { "chunk_text": query } }
                            ],
                            "filter": [
                                { "term": { "is_active": True } },
                                { "term": { "division_id": str(division_id) } }
                            ]
                        }
                    }
                },
            )

            results: List[OpenSearchResult] = []
            for hit in response["hits"]["hits"]:
                results.append(OpenSearchResult(score=hit["_score"], **hit["_source"]))

            return results
        except Exception as e:
            logger.error(f"Error searching for similar documents in OpenSearch: {e}")
            return []

    async def search_similar_vector(
        self,
        query_embedding: List[float],
        division_id: uuid.UUID,
        top_k: int = 5,
    ) -> List[OpenSearchResult]:
        """
        Vector kNN search in OpenSearch filtered by division and active docs.
        """
        try:
            body: Dict[str, Any] = {
                "size": top_k,
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"is_active": True}},
                            {"term": {"division_id": str(division_id)}}
                        ],
                        "must": {
                            "knn": {
                                "embedding": {"vector": query_embedding, "k": top_k}
                            }
                        }
                    }
                }
            }

            response = self.client.search(index=self.index_name, body=body)

            results: List[OpenSearchResult] = []
            for hit in response.get("hits", {}).get("hits", []):
                src = hit.get("_source", {})
                try:
                    results.append(
                        OpenSearchResult(
                            score=float(hit.get("_score", 0.0)),
                            chunk_text=src.get("chunk_text", ""),
                            chunk_index=int(src.get("chunk_index", 0)),
                            filename=src.get("filename", "unknown"),
                            is_active=bool(src.get("is_active", False)),
                            document_id=uuid.UUID(str(src.get("document_id"))),
                            division_id=uuid.UUID(str(src.get("division_id"))),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Skipping malformed OpenSearch hit: {e}")
            return results
        except Exception as e:
            logger.error(f"Error performing vector search in OpenSearch: {e}")
            return []

    async def update_document_active_status(self, document_id: uuid.UUID, is_active: bool) -> bool:
        """
        Update document active status in OpenSearch.
        """
        try:
            response = self.client.update_by_query(
                index=self.index_name,
                body={
                    "script": {
                        "source": "ctx._source.is_active = params.status",
                        "params": {"status": is_active}
                    },
                    "query": {
                        "term": {
                            "document_id": str(document_id)
                        }
                    }
                }
            )
            logger.info(f"OpenSearch response: {response}")
            logger.error(f"OpenSearch response: {response}")
            logger.info(f"OpenSearch document active status updated: {response}")
            return True
        except Exception as e:
            logger.error(f"Error updating document active status in OpenSearch: {e}")
            return False

    async def store_document(
        self,
        embeddings_data: List[EmbeddingData],
    ) -> bool:
        """
        Store documents in OpenSearch.
        """
        try:
            data: List[Dict[str, Any]] = []
            for embedding_data in embeddings_data:
                body: Dict[str, Any] = {
                    "chunk_text": embedding_data.chunk_text,
                    "chunk_index": embedding_data.chunk_index,
                    "document_id": embedding_data.document_id,
                }

                # Add division_id and filename if available
                if embedding_data.division_id:
                    body["division_id"] = str(embedding_data.division_id)
                if embedding_data.filename:
                    body["filename"] = embedding_data.filename
                if embedding_data.is_active is not None:
                    body["is_active"] = embedding_data.is_active
                # include vector embedding for kNN
                if embedding_data.embedding is not None:
                    body["embedding"] = embedding_data.embedding

                logger.info(f"Storing document: {body}")

                data.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": f"{embedding_data.document_id}_{embedding_data.chunk_index}"
                    }
                })
                data.append(body)

            response = self.client.bulk(
                index=self.index_name,
                body=data
            )

            logger.info(f"OpenSearch {len(data)} documents indexed: {response}")
            return True
        except Exception as e:
            logger.error(f"Error storing documents in OpenSearch: {e}")
            return False

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """
        Delete document from OpenSearch.
        """
        try:
            response = self.client.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "document_id": str(document_id)
                        }
                    }
                }
            )
            logger.info(f"OpenSearch document deleted: {response}, document_id: {document_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting document from OpenSearch: {e}")
            return False



opensearch_service = OpenSearchService()