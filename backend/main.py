"""
DocuChat AI - Backend Server
FastAPI application for RAG-based PDF question answering.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.upload_routes import router as upload_router
from routes.chat_routes import router as chat_router

# Load environment variables
load_dotenv()


from db.mongodb import mongo_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("[START] DocuChat AI Backend starting up...")
    await mongo_db.connect_db()
    print("[READY] Ready to accept PDF uploads and chat queries.")
    yield
    print("[STOP] DocuChat AI Backend shutting down...")
    await mongo_db.close_db()


app = FastAPI(
    title="DocuChat AI",
    description="RAG-based PDF Question Answering API powered by LangChain and OpenAI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload_router, tags=["Upload"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "app": "DocuChat AI",
        "version": "1.0.0",
        "message": "RAG PDF Chatbot API is running!",
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    from vector_db.vector_store import vector_store

    return {
        "status": "healthy",
        "documents_indexed": vector_store.get_document_count(),
        "mongodb_connected": mongo_db.db is not None,
    }
