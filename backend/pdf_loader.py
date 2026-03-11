"""
PDF Document Loader Module
Handles loading and splitting PDF documents into manageable chunks.
"""

import os
import tempfile
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class PDFProcessor:
    """Processes PDF files: loads content and splits into chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load a PDF file and return a list of Document objects."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for embedding."""
        chunks = self.text_splitter.split_documents(documents)
        return chunks

    async def process_uploaded_pdf(self, file_content: bytes, filename: str) -> List[Document]:
        """
        Process an uploaded PDF file:
        1. Save to a temporary file
        2. Load the PDF
        3. Split into chunks
        4. Clean up the temporary file
        """
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        # Save to temporary file
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)

        try:
            # Load and split PDF
            documents = self.load_pdf(file_path)
            chunks = self.split_documents(documents)

            # Add metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["source"] = filename
                chunk.metadata["chunk_index"] = i

            return chunks
        finally:
            # Clean up saved file (optional — keep if you want persistence)
            pass


# Singleton instance
pdf_processor = PDFProcessor()
