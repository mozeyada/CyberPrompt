from typing import Any

from bson import ObjectId


def convert_objectid(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert MongoDB ObjectId to string for Pydantic compatibility"""
    if not doc:
        return None

    # Convert all ObjectId fields to strings
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, dict):
            doc[key] = convert_objectid(value)
        elif isinstance(value, list):
            doc[key] = [convert_objectid(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]

    return doc


def convert_objectid_list(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert MongoDB ObjectIds to strings for a list of documents"""
    return [convert_objectid(doc) for doc in docs if doc]
