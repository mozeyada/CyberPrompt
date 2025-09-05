from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

security = HTTPBearer()


def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Validate API key from Authorization header"""
    if credentials.credentials not in settings.api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials


def validate_api_key_header(x_api_key: str) -> str:
    """Validate API key from x-api-key header"""
    if x_api_key not in settings.api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key
