"""Authentication endpoints: token issuance and current-user info."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from api.app.config import Settings, get_settings
from api.app.database import get_repository
from api.app.ratelimit import limited
from api.app.schemas import MeResponse, TokenResponse
from api.app.security import create_access_token, get_current_user, verify_password
from database.repository import SqliteRepository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

settings = get_settings()


@router.post("/token", response_model=TokenResponse)
@limited(settings.rate_limit)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    repository: SqliteRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    user = await repository.get_user_by_username(form.username)
    if user is None or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(
        settings, user["username"], user["role"]
    )
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=MeResponse)
async def me(user: dict = Depends(get_current_user)) -> MeResponse:
    return MeResponse(**user)
