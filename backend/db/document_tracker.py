"""
Document Tracker Service
Tracks uploaded documents in MongoDB for persistence.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from db.mongodb import mongo_db


COLLECTION_NAME = "uploaded_documents"


async def save_document_info(filename: str, chunks_count: int, file_size: int = 0):
    """Save document upload info to MongoDB."""
    if mongo_db.db is None:
        return None

    collection = mongo_db.db[COLLECTION_NAME]
    doc = {
        "filename": filename,
        "chunks_count": chunks_count,
        "file_size": file_size,
        "uploaded_at": datetime.now(timezone.utc),
    }
    result = await collection.insert_one(doc)
    return str(result.inserted_id)


async def get_all_documents() -> List[Dict]:
    """Get all uploaded documents."""
    if mongo_db.db is None:
        return []

    collection = mongo_db.db[COLLECTION_NAME]
    cursor = collection.find(
        {},
        {"_id": 0, "filename": 1, "chunks_count": 1, "file_size": 1, "uploaded_at": 1}
    ).sort("uploaded_at", -1)

    documents = []
    async for doc in cursor:
        documents.append({
            "filename": doc["filename"],
            "chunks_count": doc["chunks_count"],
            "file_size": doc.get("file_size", 0),
            "uploaded_at": doc["uploaded_at"].isoformat(),
        })
    return documents


async def get_document_count() -> int:
    """Get total number of uploaded documents."""
    if mongo_db.db is None:
        return 0

    collection = mongo_db.db[COLLECTION_NAME]
    return await collection.count_documents({})
