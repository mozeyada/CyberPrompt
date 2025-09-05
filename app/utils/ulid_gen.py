import hashlib

import ulid


def generate_ulid() -> str:
    """Generate a new ULID"""
    return str(ulid.new())


def generate_hash(content: str) -> str:
    """Generate SHA-256 hash for content"""
    return hashlib.sha256(content.encode()).hexdigest()


def generate_blob_id(content: str, run_id: str) -> str:
    """Generate unique blob ID from content and run_id"""
    combined = f"{run_id}:{content}"
    return generate_hash(combined)[:16]  # Shortened hash
