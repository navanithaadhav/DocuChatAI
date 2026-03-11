"""
RAG Pipeline Module
Orchestrates the Retrieval Augmented Generation pipeline.
"""

import os
from typing import Dict, List

from dotenv import load_dotenv
import warnings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate

# Suppress LangChain deprecation warnings for cleaner logs
warnings.filterwarnings("ignore", category=DeprecationWarning)

from vector_db.vector_store import vector_store

load_dotenv()


# Custom prompt template for the RAG chain
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    """Given the following conversation and a follow up question, rephrase the follow up question 
to be a standalone question that captures the full context.

Chat History:
{chat_history}

Follow Up Input: {question}

Standalone question:"""
)

QA_PROMPT = PromptTemplate.from_template(
    """You are DocuChat AI, an intelligent assistant that answers questions based on the provided document context.

INSTRUCTIONS:
- Answer the question based on the provided context.
- If the context doesn't contain the specific answer but relates to it, try to be as helpful as possible using the provided info.
- If the context doesn't contain any relevant information at all, say: "I couldn't find relevant information in the uploaded documents to answer this question. Please try rephrasing your question or upload additional documents."
- Be thorough, precise, and helpful.
- Use bullet points or numbered lists.

Context from documents:
{context}

Question: {question}

Helpful Answer:"""
)


class RAGPipeline:
    """Manages the RAG pipeline for question answering over documents."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key is None:
            self.api_key = os.getenv("GOOGLE_API_KEY") # fallback
            
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",  # Using flash-latest for stable availability and quota
            google_api_key=self.api_key,
            temperature=0.1,  # Lower temperature for faster/more stable technical answers
            max_tokens=1024,
        )

        # Conversation memory (keeps last 5 exchanges)
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            k=5,
        )

        self.chain = None
        self._build_chain()

    def _build_chain(self):
        """Build the conversational retrieval chain."""
        retriever = vector_store.get_retriever(k=4)

        if retriever is None:
            return

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True,
            verbose=False,
        )

    def rebuild_chain(self):
        """Rebuild the chain (call after adding new documents)."""
        # Memory is preserved so context is not lost across document uploads
        # self.memory.clear() 
        self._build_chain()

    async def ask(self, question: str) -> Dict:
        """Ask a question and get an AI-generated answer based on document context."""
        if self.chain is None:
            self._build_chain()

        if self.chain is None:
            return {
                "answer": "No documents have been uploaded yet. Please upload a PDF document first.",
                "sources": [],
            }

        try:
            # Robust retry logic with exponential backoff
            max_retries = 5
            base_delay = 1
            result = None
            last_error = None

            for attempt in range(max_retries):
                try:
                    result = self.chain.invoke({"question": question})
                    break
                except Exception as e:
                    last_error = e
                    if "500" in str(e) or "INTERNAL" in str(e):
                        import asyncio
                        import random
                        # Exponential backoff: 1s, 2s, 4s, 8s... + jitter
                        delay = (base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
                        print(f"[RETRY] Attempt {attempt + 1} failed with 500 error. Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                        continue
                    raise e

            if result is None:
                raise last_error if last_error else Exception("Unknown error in RAG chain")

            # Extract source information
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_info = {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", "N/A"),
                    }
                    sources.append(source_info)

            return {
                "answer": result.get("answer", "I could not generate a response."),
                "sources": sources,
            }

        except Exception as e:
            error_msg = str(e)
            if "500" in error_msg or "INTERNAL" in error_msg:
                error_msg = "Google's embedding service is currently unstable (500 Internal Error). I tried retrying 5 times but the service is still unresponsive. This is a temporary server-side issue at Google. Please try again in 1-2 minutes."
            
            return {
                "answer": f"Processing error: {error_msg}",
                "sources": [],
            }

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()


# Singleton instance
rag_pipeline = RAGPipeline()
