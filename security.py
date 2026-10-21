import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

load_dotenv(Path(__file__).resolve().parent / ".env")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)

def require_api_key(
    provided_key: str | None = Depends(api_key_header),
) -> None:
    expected_key = os.getenv("API_KEY")

    if not expected_key:
        raise RuntimeError("API_KEY is not configured")

    if not provided_key or not secrets.compare_digest(
        provided_key, expected_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
