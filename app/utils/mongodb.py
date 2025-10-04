from typing import Any
import math

from bson import ObjectId


def safe_float(value: Any) -> Any:
    """Convert NaN and Infinity values to None for JSON serialization"""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def convert_objectid(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert MongoDB ObjectId to string for Pydantic compatibility and sanitize float values"""
    if not doc:
        return None

    # Convert all ObjectId fields to strings and sanitize float values
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, float):
            doc[key] = safe_float(value)
        elif isinstance(value, dict):
            doc[key] = convert_objectid(value)
        elif isinstance(value, list):
            doc[key] = [convert_objectid(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else safe_float(item) for item in value]

    return doc


def convert_objectid_list(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert MongoDB ObjectIds to strings for a list of documents"""
    return [convert_objectid(doc) for doc in docs if doc]
