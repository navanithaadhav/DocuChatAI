"""
Embeddings Module
Handles generating embeddings using Google's generative AI embedding model.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

load_dotenv()


class EmbeddingManager:
    """Manages embedding generation using Google Gemini."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key is None:
            self.api_key = os.getenv("GOOGLE_API_KEY") # fallback
            
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")

        # Using gemini-embedding-2-preview for better stability
        # It maintains the 3072 dimensions required by your Pinecone index
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2-preview",
            google_api_key=self.api_key,
            task_type="retrieval_query",
        )

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Return the embeddings instance."""
        return self.embeddings


# Singleton instance
embedding_manager = EmbeddingManager()
