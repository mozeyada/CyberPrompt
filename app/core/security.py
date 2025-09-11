from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

# Convert API keys to set for O(1) lookup
_API_KEYS_SET = set(settings.api_keys)

security = HTTPBearer()


def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Validate API key from Authorization header"""
    if credentials.credentials not in _API_KEYS_SET:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials


def validate_api_key_header(x_api_key: str) -> str:
    """Validate API key from x-api-key header"""
    if x_api_key not in _API_KEYS_SET:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key
