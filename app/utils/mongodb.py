from typing import Any

from bson import ObjectId


def convert_objectid(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert MongoDB ObjectId to string for Pydantic compatibility"""
    if not doc:
        return None

    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])

    return doc


def convert_objectid_list(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert MongoDB ObjectIds to strings for a list of documents"""
    return [convert_objectid(doc) for doc in docs if doc]
