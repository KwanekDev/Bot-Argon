from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import hash_api_key
from app.modules.authentication.application.interfaces import (
    ApiKeyRepository,
    UserRepository,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.infrastructure.repositories import (
    SqlAlchemyApiKeyRepository,
    SqlAlchemyUserRepository,
)


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_api_key_repository(
    session: AsyncSession = Depends(get_session),
) -> ApiKeyRepository:
    return SqlAlchemyApiKeyRepository(session)


def get_auth_use_cases(
    users: UserRepository = Depends(get_user_repository),
    keys: ApiKeyRepository = Depends(get_api_key_repository),
) -> AuthenticationUseCases:
    return AuthenticationUseCases(users, keys)


async def require_api_key(
    x_api_key: str | None = Header(default=None),
    keys: ApiKeyRepository = Depends(get_api_key_repository),
) -> dict:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-API-Key header",
        )
    entity = await keys.get_by_hash(hash_api_key(x_api_key))
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return {"id": entity.id, "name": entity.name, "scopes": entity.scopes}

