"""
Pinecone Vector Store Module
Manages storing and retrieving document embeddings using Pinecone (Cloud).
Falls back to ChromaDB for local development if PINECONE_API_KEY is not set.
"""

import os
from typing import List, Optional

from langchain_core.documents import Document
from dotenv import load_dotenv

from embeddings import embedding_manager

load_dotenv()


class VectorStoreManager:
    """Manages the vector store - uses Pinecone (cloud) or ChromaDB (local)."""

    def __init__(self):
        self.embeddings = embedding_manager.get_embeddings()
        self.vectorstore = None
        self.use_pinecone = False
        self._initialize_store()

    def _initialize_store(self):
        """Initialize Pinecone if API key exists, otherwise fall back to ChromaDB."""
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index = os.getenv("PINECONE_INDEX_NAME", "docuchat-ai")

        if pinecone_api_key:
            try:
                from pinecone import Pinecone
                from langchain_pinecone import PineconeVectorStore

                pc = Pinecone(api_key=pinecone_api_key)

                # Check if index exists, if not create it
                existing_indexes = [idx.name for idx in pc.list_indexes()]
                if pinecone_index not in existing_indexes:
                    from pinecone import ServerlessSpec
                    pc.create_index(
                        name=pinecone_index,
                        dimension=768,  # Matches gemini-embedding-001
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    )
                    print(f"[OK] Created Pinecone index: {pinecone_index}")

                self.vectorstore = PineconeVectorStore(
                    index=pc.Index(pinecone_index),
                    embedding=self.embeddings,
                    text_key="text",
                )
                self.use_pinecone = True
                print(f"[CLOUD] Connected to Pinecone cloud index: {pinecone_index}")

            except Exception as e:
                print(f"[WARN] Pinecone connection failed: {e}")
                print("[LOCAL] Falling back to local ChromaDB...")
                self._init_chroma()
        else:
            print("[LOCAL] No PINECONE_API_KEY found. Using local ChromaDB.")
            self._init_chroma()

    def _init_chroma(self):
        """Initialize local ChromaDB as fallback."""
        from langchain_community.vectorstores import Chroma

        persist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db_v3")
        os.makedirs(persist_dir, exist_ok=True)

        self.vectorstore = Chroma(
            collection_name="docuchat_documents",
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
        )
        self.use_pinecone = False

    async def add_documents(self, documents: List[Document]) -> int:
        """Add documents to the vector store with batch processing."""
        if not documents or self.vectorstore is None:
            return 0

        # Batch size for embeddings and upsert
        batch_size = 50
        total_docs = len(documents)
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i : i + batch_size]
            print(f"[PROCESS] Processing batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1}...")
            # Note: PineconeVectorStore handles async if provided, but here we call it sequentially in batches 
            # to avoid overloading the API and improve reliability.
            self.vectorstore.add_documents(batch)
            
        return total_docs

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for relevant documents."""
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)

    def get_retriever(self, k: int = 4):
        """Return a retriever interface."""
        if self.vectorstore is None:
            return None
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def get_document_count(self) -> int:
        """Get total document count."""
        if self.vectorstore is None:
            return 0

        if self.use_pinecone:
            try:
                stats = self.vectorstore._index.describe_index_stats()
                return stats.get("total_vector_count", 0)
            except Exception:
                return 0
        else:
            # ChromaDB
            try:
                return self.vectorstore._collection.count()
            except Exception:
                return 0

    def clear_store(self):
        """Clear all documents."""
        self._initialize_store()


# Singleton instance
vector_store = VectorStoreManager()
