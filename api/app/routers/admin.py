"""Admin/service endpoints protected by API keys."""
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status

from api.app.database import get_repository
from api.app.security import hash_api_key, verify_api_key
from database.repository import SqliteRepository

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


async def require_api_key(
    x_api_key: str | None = Header(default=None),
    repository: SqliteRepository = Depends(get_repository),
) -> dict:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-API-Key header",
        )
    stored = await repository.get_api_key_by_hash(hash_api_key(x_api_key))
    if stored is None or not verify_api_key(x_api_key, stored["key_hash"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return stored


@router.get("/health")
async def admin_health(
    api_key: dict = Depends(require_api_key),
    repository: SqliteRepository = Depends(get_repository),
) -> dict:
    await repository.ping()
    return {"status": "ok", "database": "connected"}
