"""Warn listing endpoint."""
from fastapi import APIRouter, Depends

from api.app.database import get_repository
from api.app.schemas import WarnOut
from api.app.security import get_current_user
from database.repository import SqliteRepository

router = APIRouter(tags=["warns"])


@router.get("/api/v1/warns", response_model=list[WarnOut])
async def list_warns(
    user: dict = Depends(get_current_user),
    repository: SqliteRepository = Depends(get_repository),
) -> list[WarnOut]:
    rows = await repository.list_warns()
    return [WarnOut(**row) for row in rows]
