"""
Chat Routes
Handles chat interactions with the RAG pipeline.
"""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from rag_pipeline import rag_pipeline
from vector_db.vector_store import vector_store
from db.chat_history import save_chat_message, get_chat_history, get_all_sessions, delete_session

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    content: str
    source: str
    page: str | int


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    total_documents: int
    session_id: str


class ClearMemoryResponse(BaseModel):
    message: str


class SessionInfo(BaseModel):
    session_id: str
    last_message: str
    last_role: str
    updated_at: str
    message_count: int


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    sources: List[dict]
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a question and get an AI-generated answer based on uploaded documents."""

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Generate or use existing session
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # Save user message to MongoDB
        await save_chat_message(session_id, "user", request.question)

        result = await rag_pipeline.ask(request.question)

        # Save AI response to MongoDB
        await save_chat_message(session_id, "assistant", result["answer"], result["sources"])

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            total_documents=vector_store.get_document_count(),
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}",
        )


@router.get("/chat/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """Get all chat sessions."""
    sessions = await get_all_sessions()
    return sessions


@router.get("/chat/history/{session_id}", response_model=List[ChatHistoryMessage])
async def get_session_history(session_id: str):
    """Get chat history for a specific session."""
    history = await get_chat_history(session_id)
    return history


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    count = await delete_session(session_id)
    return {"message": f"Deleted {count} messages from session.", "deleted_count": count}


@router.post("/clear-memory", response_model=ClearMemoryResponse)
async def clear_memory():
    """Clear conversation memory."""
    rag_pipeline.clear_memory()
    return ClearMemoryResponse(message="Conversation memory cleared successfully.")

