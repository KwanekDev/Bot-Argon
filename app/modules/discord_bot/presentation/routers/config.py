"""Admin API: bot runtime config (presence etc.)."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.authentication.presentation.routers import require_admin
from app.modules.discord_bot.infrastructure.flags import SqlAlchemyBotFlagRepository

router = APIRouter(prefix="/api/v1/admin/bot-config", tags=["bot-config"])

ALLOWED = {"presence_activity", "presence_type", "presence_status", "strefa_ping_role"}


class BotConfigOut(BaseModel):
    presence_activity: str = ""
    presence_type: str = ""
    presence_status: str = ""
    strefa_ping_role: str = ""


class BotConfigPatch(BaseModel):
    presence_activity: str | None = None
    presence_type: str | None = None
    presence_status: str | None = None
    strefa_ping_role: str | None = None


@router.get("", response_model=BotConfigOut)
async def get_config(
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> BotConfigOut:
    repo = SqlAlchemyBotFlagRepository(session)
    data = {}
    for key in ALLOWED:
        data[key] = await repo.get(key) or ""
    return BotConfigOut(**data)


@router.patch("", response_model=BotConfigOut)
async def patch_config(
    payload: BotConfigPatch,
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> BotConfigOut:
    repo = SqlAlchemyBotFlagRepository(session)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key not in ALLOWED:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Field not allowed")
        await repo.set(key, str(value))
    data = {}
    for key in ALLOWED:
        data[key] = await repo.get(key) or ""
    return BotConfigOut(**data)

