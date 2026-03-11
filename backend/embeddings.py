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

        # Defaulting to 'embedding-001' or 'text-embedding-004' for better baseline stability.
        # Note: 'gemini-embedding-2-preview' has 3072 dimensions, while
        # 'text-embedding-004' and 'embedding-001' use 768 dimensions.
        # Ensure your vector store index dimension matches!
        
        self.model_name = "models/text-embedding-004" # 768 dimensions
        
        # If the user explicitly wants the high-dim preview model
        # self.model_name = "models/gemini-embedding-2-preview" # 3072 dimensions

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model_name,
            google_api_key=self.api_key,
            task_type="retrieval_query",
        )

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Return the embeddings instance."""
        return self.embeddings


# Singleton instance
embedding_manager = EmbeddingManager()
