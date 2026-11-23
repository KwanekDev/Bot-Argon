from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.ratelimit import limited
from app.core.security import create_access_token, get_current_user
from app.core.settings import Settings, get_settings
from app.modules.authentication.application.exceptions import ApiKeyNotFoundError
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.presentation.dependencies import (
    get_auth_use_cases,
    require_api_key,
)
from app.modules.authentication.presentation.schemas import (
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyOut,
    MeResponse,
    TokenResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


@router.post("/token", response_model=TokenResponse)
@limited(get_settings().rate_limit)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    use_cases: AuthenticationUseCases = Depends(get_auth_use_cases),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    try:
        user = await use_cases.authenticate(form.username, form.password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(settings, user.username, user.role)
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=MeResponse)
async def me(user: dict = Depends(get_current_user)) -> MeResponse:
    return MeResponse(**user)


@admin_router.get("/health")
async def admin_health(
    api_key: dict = Depends(require_api_key),
    session: AsyncSession = Depends(get_session),
) -> dict:
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@admin_router.post("/api-keys", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    admin: dict = Depends(require_admin),
    use_cases: AuthenticationUseCases = Depends(get_auth_use_cases),
) -> ApiKeyCreated:
    entity, raw = await use_cases.issue_api_key_for_username(admin["username"], payload.name)
    return ApiKeyCreated(id=entity.id, name=entity.name, key=raw)


@admin_router.get("/api-keys", response_model=list[ApiKeyOut])
async def list_api_keys(
    admin: dict = Depends(require_admin),
    use_cases: AuthenticationUseCases = Depends(get_auth_use_cases),
) -> list[ApiKeyOut]:
    entities = await use_cases.list_api_keys_for_username(admin["username"])
    return [
        ApiKeyOut(
            id=e.id, name=e.name, scopes=e.scopes, created_at=str(e.created_at)
        )
        for e in entities
    ]


@admin_router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    admin: dict = Depends(require_admin),
    use_cases: AuthenticationUseCases = Depends(get_auth_use_cases),
) -> None:
    removed = await use_cases.revoke_api_key_for_username(admin["username"], key_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")


@admin_router.post("/api-keys/{key_id}/rotate", response_model=ApiKeyCreated)
async def rotate_api_key(
    key_id: int,
    admin: dict = Depends(require_admin),
    use_cases: AuthenticationUseCases = Depends(get_auth_use_cases),
) -> ApiKeyCreated:
    try:
        entity, raw = await use_cases.rotate_api_key_for_username(admin["username"], key_id)
    except ApiKeyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return ApiKeyCreated(id=entity.id, name=entity.name, key=raw)

