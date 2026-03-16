"""API key authentication dependency for admin endpoints."""
import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def require_api_key(api_key: str = Security(_api_key_header)) -> None:
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="ADMIN_API_KEY is not configured on this server.",
        )
    if api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key.")
