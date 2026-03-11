"""
Upload Routes
Handles PDF document upload and processing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from pdf_loader import pdf_processor
from vector_db.vector_store import vector_store
from rag_pipeline import rag_pipeline
from db.document_tracker import save_document_info

router = APIRouter()


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_processed: int
    total_documents: int


@router.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a single PDF document (legacy)."""
    return await process_files([file])

@router.post("/upload-pdfs", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload and process multiple PDF documents."""
    return await process_files(files)

async def process_files(files: List[UploadFile]):
    total_added = 0
    processed_files = []
    
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
            
        contents = await file.read()
        max_size = 20 * 1024 * 1024  # 20MB
        if len(contents) > max_size or len(contents) == 0:
            continue
            
        try:
            chunks = await pdf_processor.process_uploaded_pdf(contents, file.filename)
            if chunks:
                num_added = vector_store.add_documents(chunks)
                total_added += num_added
                processed_files.append(file.filename)
                
                # Track in MongoDB
                await save_document_info(
                    filename=file.filename,
                    chunks_count=num_added,
                    file_size=len(contents),
                )
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            continue

    if not processed_files:
        raise HTTPException(
            status_code=400,
            detail="Could not process any of the uploaded PDF files. Please check if they are valid.",
        )

    # Rebuild the RAG chain
    rag_pipeline.rebuild_chain()

    filename_str = ", ".join(processed_files)
    if len(filename_str) > 50:
        filename_str = f"{len(processed_files)} PDF files"

    return UploadResponse(
        message=f"Successfully processed {len(processed_files)} file(s)",
        filename=filename_str,
        chunks_processed=total_added,
        total_documents=vector_store.get_document_count(),
    )

