"""
RAG (Retrieval Augmented Generation) pipeline service.
"""
import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID
import openai
from loguru import logger

from ..config import settings
from ..models import SimilarChunk, ChatResult
import httpx
from ..database import db_manager
from .embedder import embedding_service
from .text_cleaner import text_cleaner
from .hybrid_retriever import hybrid_retriever


class RAGService:
    """Retrieval Augmented Generation service."""
    
    def __init__(self):
        """Initialize the RAG service."""
        self.top_k = settings.top_k_results
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.llm_model = settings.llm_model
        
        # Initialize LLM client based on configuration
        if settings.use_openrouter and settings.openrouter_api_key:
            # Use OpenRouter for LLM calls
            self.openai_client = openai.OpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url
            )
            logger.info(f"Initialized RAG service with OpenRouter LLM model: {self.llm_model}")
        elif settings.openai_api_key:
            # Use OpenAI directly for LLM calls
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            logger.info(f"Initialized RAG service with OpenAI LLM model: {self.llm_model}")
        else:
            self.openai_client = None
            logger.warning("No API key provided - chat functionality will be limited")
    
    async def process_chat_query(
        self,
        division_id: UUID,
        query: str,
        conversation_id: Optional[UUID] = None,
        title: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Optional[ChatResult]:
        """
        Process a chat query using the RAG pipeline.
        
        Args:
            division_id: UUID of the division to search in
            query: User query text
            
        Returns:
            ChatResult with answer and sources, or None if error
        """
        try:
            logger.info(f"Processing chat query for division {division_id}: {query[:100]}...")
            
            # Step 1: Clean the query for better matching
            cleaned_query = text_cleaner.clean_query_text(query)
            logger.info(f"Cleaned query: '{cleaned_query}'")
            
            # Extract key terms for enhanced retrieval
            key_terms = text_cleaner.extract_key_terms(query, max_terms=5)
            if key_terms:
                logger.info(f"Key terms extracted: {key_terms}")
                # Enhance query with key terms if they're not already present
                enhanced_query = self._enhance_query_with_terms(cleaned_query, key_terms)
                logger.info(f"Enhanced query: '{enhanced_query}'")
            else:
                enhanced_query = cleaned_query
            
            # Step 2: Generate query embedding using the enhanced query
            query_embedding = await embedding_service.generate_query_embedding(enhanced_query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return None
            
            # Step 3: Retrieve similar chunks using hybrid search
            similar_chunks = await self._retrieve_similar_chunks_hybrid(
                query, query_embedding, division_id
            )

            similar_filename_chunks = set()
            for chunk in similar_chunks:
                similar_filename_chunks.add(chunk.filename)
            
            # Step 3.5: Fetch conversation history from Express (optional)
            history_messages: List[Dict[str, Any]] = []
            if settings.internal_api_key and conversation_id:
                try:
                    url = f"{settings.express_api_url}/api/v1/conversations/{conversation_id}/history-internal?limit={settings.conversation_history_limit}"
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get(url, headers={"x-internal-api-key": settings.internal_api_key})
                        if resp.status_code == 200:
                            payload = resp.json()
                            history_messages = payload.get("data", {}).get("messages", [])
                        else:
                            logger.warning(f"History fetch non-200: {resp.status_code}")
                except Exception as e:
                    logger.warning(f"Failed to fetch conversation history: {e}")

            # Step 4: Generate answer using LLM (use original query for context) + history
            answer = await self._generate_answer(query, similar_chunks, history_messages, division_id)
            if not answer:
                logger.error("Failed to generate answer")
                return None
            
            # Step 5: Create result
            result = ChatResult(
                query=query,
                answer=answer,
                sources=similar_chunks,
                division_id=division_id,
                model_used=self.llm_model
            )
            
            # Step 6: (New conversation) generate a concise title using LLM
            generated_title: Optional[str] = None
            logger.info(f"Internal API key: {settings.internal_api_key}")
            logger.info(f"Conversation ID: {conversation_id}")
            if settings.internal_api_key and not conversation_id:
                try:
                    generated_title = await self._generate_title(query, result.answer)
                except Exception as e:
                    logger.warning(f"Failed to generate conversation title: {e}")

            # Step 7: Ingest conversation messages back to Express
            if settings.internal_api_key:
                try:
                    ingest_url = f"{settings.express_api_url}/api/v1/conversations/ingest"
                    body: Dict[str, Any] = {
                        "messages": [
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": answer, "sources": ",".join([filename for filename in similar_filename_chunks])},
                        ],
                        "division_id": str(division_id),
                    }
                    if conversation_id:
                        body["conversation_id"] = str(conversation_id)
                    else:
                        body["title"] = (generated_title or title or query[:60])
                        if user_id:
                            body["user_id"] = str(user_id)

                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.post(ingest_url, json=body, headers={"x-internal-api-key": settings.internal_api_key})
                        if resp.status_code in (200, 201):
                            try:
                                data = resp.json().get("data", {})
                                conv_id = data.get("conversation_id")
                                if conv_id:
                                    result.conversation_id = conv_id
                            except Exception:
                                pass
                        else:
                            logger.warning(f"Conversation ingest non-2xx: {resp.status_code}")
                except Exception as e:
                    logger.warning(f"Failed to ingest conversation messages: {e}")
            
            logger.info("Successfully processed chat query")
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return None
    
    async def _retrieve_similar_chunks_hybrid(
        self, 
        query: str,
        query_embedding: List[float], 
        division_id: UUID
    ) -> List[SimilarChunk]:
        """
        Retrieve similar chunks using hybrid search (vector + BM25).
        
        Args:
            query: Original query text
            query_embedding: Query embedding vector
            division_id: Division to search in
            
        Returns:
            List of similar chunks
        """
        try:
            logger.info(f"Searching for similar chunks in division {division_id} using hybrid search")
            
            # Use hybrid retriever for better results
            similar_chunks = await hybrid_retriever.search(
                query=query,
                query_embedding=query_embedding,
                division_id=division_id,
                top_k=self.top_k
            )
            
            logger.info(f"Found {len(similar_chunks)} similar chunks using hybrid search")
            logger.info(f"Similar chunks: {similar_chunks}")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving similar chunks with hybrid search: {e}")
            # Fallback to vector-only search
            return await self._retrieve_similar_chunks_fallback(query_embedding, division_id)
    
    async def _retrieve_similar_chunks_fallback(
        self, 
        query_embedding: List[float], 
        division_id: UUID
    ) -> List[SimilarChunk]:
        """
        Fallback method to retrieve similar chunks using vector search only.
        
        Args:
            query_embedding: Query embedding vector
            division_id: Division to search in
            
        Returns:
            List of similar chunks
        """
        try:
            logger.info(f"Fallback: Searching for similar chunks in division {division_id} using vector search")
            
            # Search database for similar embeddings
            results = await db_manager.search_similar_embeddings(
                query_embedding, division_id, self.top_k
            )
            
            # Convert to SimilarChunk objects
            similar_chunks = []
            for result in results:
                chunk = SimilarChunk(
                    chunk_text=result["chunk_text"],
                    chunk_index=result["chunk_index"],
                    filename=result["filename"],
                    distance=result["distance"]
                )
                similar_chunks.append(chunk)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks using fallback vector search")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving similar chunks with fallback: {e}")
            return []
    
    async def _generate_answer(
        self,
        query: str,
        similar_chunks: List[SimilarChunk],
        history_messages: List[Dict[str, Any]],
        division_id: UUID
    ) -> Optional[str]:
        """
        Generate answer using LLM based on query and retrieved chunks.
        
        Args:
            query: User query
            similar_chunks: Retrieved similar chunks
            
        Returns:
            Generated answer, or None if error
        """
        try:
            if not self.openai_client:
                logger.error("OpenAI client not initialized - cannot generate answer")
                return None
            
            # Construct prompt
            prompt = await self._construct_prompt(query, similar_chunks, history_messages, division_id)
            logger.info(f"Constructed prompt with {len(similar_chunks)} chunks")
            
            # Generate answer using OpenAI
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a helpful assistant that answers questions based on the provided context. \
                        Answer or state with bahasa Indonesia. \ 
                        If you cannot find the answer in the context, say so clearly. \
                        If task given is not related to the available documents or context, say 'Maaf, saya tidak dapat menjawab pertanyaan Anda dikarenakan tidak ada informasi yang relevan dalam pemahaman saya.' in the respective language. \
                        Response with rich Markdown as valid GitHub-flavored Markdown format, do separate each sentence with 2 new line (USE '\\n\\n') instead of one and make sure when implementing bold, italic, underline, etc, use the correct syntax and make sure when implementing table-like structure, use the correct syntax."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer of length {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return None
    
    async def _construct_prompt(
        self,
        query: str,
        similar_chunks: List[SimilarChunk],
        history_messages: List[Dict[str, Any]],
        division_id: UUID
    ) -> str:
        """
        Construct prompt for LLM with query and context.
        
        Args:
            query: User query
            similar_chunks: Retrieved chunks to use as context
            history_messages: Conversation history
            division_id: Division ID to get available documents
            
        Returns:
            Constructed prompt
        """
        # Get all available documents in the division
        available_documents = await db_manager.get_documents_by_division(division_id)
        
        # Build context from similar chunks
        context_parts = []
        for i, chunk in enumerate(similar_chunks, 1):
            context_parts.append(
                f"Context {i} (from {chunk.filename}):\n{chunk.chunk_text}\n"
            )
        
        context = "\n".join(context_parts)

        # Build concise conversation history (most recent last)
        history_parts = []
        for m in history_messages[-settings.conversation_history_limit:]:
            role = m.get("role", "user")
            content = m.get("content", "")
            history_parts.append(f"{role}: {content}")
        history = "\n".join(history_parts)

        # Build available documents list
        available_docs_parts = []
        if available_documents:
            available_docs_parts.append("Available documents in this division:")
            for doc in available_documents:
                available_docs_parts.append(f"- {doc['original_filename']} ({doc['file_type']})")
        else:
            available_docs_parts.append("No documents are currently available in this division.")
        
        available_docs = "\n".join(available_docs_parts)

        # Construct final prompt
        prompt = (
            "You are a helpful assistant. Answer in bahasa Indonesia.\n\n"
            "Conversation history (most recent last):\n"
            f"{history}\n\n"
            f"Available documents: {available_docs}\n\n"
            "Use the following retrieved document context to answer the new user question.\n"
            "If the answer is not in the context, say you don't have enough information.\n\n"
            f"Context:\n{context}\n\n"
            f"New Question: {query}\n\n"
            "Answer:"
        )
        
        return prompt

    async def _generate_title(self, query: str, answer: str) -> Optional[str]:
        """Generate a short conversation title from query and answer using the LLM."""
        try:
            if not self.openai_client:
                return None

            system = (
                "Create a short, descriptive title (max 8 words) for this conversation. Query and answer are provided."
                "Return only the title, no quotes, no reason, no explanation, no nothing."
                "Use bahasa Indonesia."
            )
            user = f"Query: {query}\nAnswer: {answer}"
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=self.max_tokens, # if set to 24 then it will return nothing as the llm use reasoning so if we set to 24, it effect the reasoning process.
                temperature=0.3,
            )
            title = response.choices[0].message.content.strip()
            # Trim excessively long titles as a safeguard
            if len(title) > 80:
                title = title[:80]
            return title
        except Exception as e:
            logger.warning(f"Title generation failed: {e}")
            return None
    
    async def _log_interaction(
        self, 
        division_id: UUID, 
        query: str, 
        answer: str
    ) -> None:
        """
        Log the chat interaction to the database.
        
        Args:
            division_id: Division ID
            query: User query
            answer: Generated answer

            
        """
        try:
            await db_manager.log_user_query(
                division_id=division_id,
                query_text=query,
                response_text=answer
            )
            logger.info("Logged chat interaction to database")
        except Exception as e:
            logger.warning(f"Failed to log interaction: {e}")
    
    def _enhance_query_with_terms(self, query: str, key_terms: List[str]) -> str:
        """
        Enhance query with key terms if they provide additional context.
        
        Args:
            query: Cleaned query text
            key_terms: Extracted key terms
            
        Returns:
            Enhanced query text
        """
        if not key_terms:
            return query
        
        # Convert query to lowercase for comparison
        query_lower = query.lower()
        
        # Find key terms that aren't already in the query
        missing_terms = []
        for term in key_terms:
            if term.lower() not in query_lower:
                missing_terms.append(term)
        
        # Add up to 2 missing terms to avoid making query too long
        if missing_terms:
            additional_terms = missing_terms[:2]
            enhanced_query = f"{query} {' '.join(additional_terms)}"
            return enhanced_query.strip()
        
        return query
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the RAG service configuration."""
        llm_provider = "None"
        if self.openai_client is not None:
            if settings.use_openrouter:
                llm_provider = "OpenRouter"
            else:
                llm_provider = "OpenAI"
        
        return {
            "llm_model": self.llm_model,
            "llm_provider": llm_provider,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_k_results": self.top_k,
            "embedding_service": embedding_service.get_model_info(),
            "llm_available": self.openai_client is not None,
            "openrouter_enabled": settings.use_openrouter
        }


# Global RAG service instance
rag_service = RAGService()
