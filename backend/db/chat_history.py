"""
Chat History Service
Stores and retrieves chat conversations in MongoDB.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from db.mongodb import mongo_db


COLLECTION_NAME = "chat_history"


async def save_chat_message(session_id: str, role: str, content: str, sources: List[Dict] = None):
    """Save a single chat message to MongoDB."""
    if mongo_db.db is None:
        return None

    collection = mongo_db.db[COLLECTION_NAME]
    message = {
        "session_id": session_id,
        "role": role,  # "user" or "assistant"
        "content": content,
        "sources": sources or [],
        "timestamp": datetime.now(timezone.utc),
    }
    result = await collection.insert_one(message)
    return str(result.inserted_id)


async def get_chat_history(session_id: str, limit: int = 50) -> List[Dict]:
    """Retrieve chat history for a session."""
    if mongo_db.db is None:
        return []

    collection = mongo_db.db[COLLECTION_NAME]
    cursor = collection.find(
        {"session_id": session_id},
        {"_id": 0, "role": 1, "content": 1, "sources": 1, "timestamp": 1}
    ).sort("timestamp", 1).limit(limit)

    messages = []
    async for doc in cursor:
        messages.append({
            "role": doc["role"],
            "content": doc["content"],
            "sources": doc.get("sources", []),
            "timestamp": doc["timestamp"].isoformat(),
        })
    return messages


async def get_all_sessions() -> List[Dict]:
    """Get all unique session IDs with their latest message."""
    if mongo_db.db is None:
        return []

    collection = mongo_db.db[COLLECTION_NAME]
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$first": "$content"},
            "last_role": {"$first": "$role"},
            "updated_at": {"$first": "$timestamp"},
            "message_count": {"$sum": 1},
        }},
        {"$sort": {"updated_at": -1}},
        {"$limit": 20},
    ]
    sessions = []
    async for doc in collection.aggregate(pipeline):
        sessions.append({
            "session_id": doc["_id"],
            "last_message": doc["last_message"][:100],
            "last_role": doc["last_role"],
            "updated_at": doc["updated_at"].isoformat(),
            "message_count": doc["message_count"],
        })
    return sessions


async def delete_session(session_id: str) -> int:
    """Delete all messages in a session."""
    if mongo_db.db is None:
        return 0

    collection = mongo_db.db[COLLECTION_NAME]
    result = await collection.delete_many({"session_id": session_id})
    return result.deleted_count
