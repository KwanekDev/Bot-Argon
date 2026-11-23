from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.modules.warns.application.use_cases import WarnUseCases
from app.modules.warns.presentation.dependencies import get_warn_use_cases
from app.modules.warns.presentation.schemas import WarnOut

router = APIRouter(tags=["warns"])


@router.get("/api/v1/warns", response_model=list[WarnOut])
async def list_warns(
    user: dict = Depends(get_current_user),
    use_cases: WarnUseCases = Depends(get_warn_use_cases),
) -> list[WarnOut]:
    entities = await use_cases.list_all()
    return [
        WarnOut(
            id=e.id,
            user_id=int(e.user_id),
            server_id=int(e.server_id),
            moderator_id=int(e.moderator_id),
            reason=e.reason,
            created_at=str(e.created_at),
        )
        for e in entities
    ]

