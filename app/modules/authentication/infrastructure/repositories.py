from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.authentication.application.interfaces import (
    ApiKeyRepository,
    UserRepository,
)
from app.modules.authentication.domain.entities import ApiKeyEntity, UserEntity
from app.modules.authentication.infrastructure.models import ApiKey, User


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> UserEntity | None:
        result = await self._session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserEntity(
            id=user.id,
            username=user.username,
            role=user.role,
            password_hash=user.password_hash,
        )

    async def create(
        self, username: str, password_hash: str, role: str = "user"
    ) -> UserEntity:
        user = User(username=username, password_hash=password_hash, role=role)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return UserEntity(
            id=user.id,
            username=user.username,
            role=user.role,
            password_hash=user.password_hash,
        )


class SqlAlchemyApiKeyRepository(ApiKeyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str, key_hash: str, owner_id: int) -> ApiKeyEntity:
        key = ApiKey(name=name, key_hash=key_hash, owner_id=owner_id)
        self._session.add(key)
        await self._session.commit()
        await self._session.refresh(key)
        return ApiKeyEntity(
            id=key.id,
            name=key.name,
            key_hash=key.key_hash,
            owner_id=key.owner_id,
            scopes=key.scopes,
            created_at=key.created_at,
        )

    async def get_by_hash(self, key_hash: str) -> ApiKeyEntity | None:
        result = await self._session.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        key = result.scalar_one_or_none()
        if key is None:
            return None
        return ApiKeyEntity(
            id=key.id,
            name=key.name,
            key_hash=key.key_hash,
            owner_id=key.owner_id,
            scopes=key.scopes,
            created_at=key.created_at,
        )

    async def list_for_user(self, owner_id: int) -> list[ApiKeyEntity]:
        result = await self._session.execute(
            select(ApiKey).where(ApiKey.owner_id == owner_id).order_by(ApiKey.id)
        )
        rows = result.scalars().all()
        return [
            ApiKeyEntity(
                id=k.id,
                name=k.name,
                key_hash=k.key_hash,
                owner_id=k.owner_id,
                scopes=k.scopes,
                created_at=k.created_at,
            )
            for k in rows
        ]

    async def delete(self, key_id: int, owner_id: int) -> bool:
        result = await self._session.execute(
            delete(ApiKey).where(ApiKey.id == key_id, ApiKey.owner_id == owner_id)
        )
        await self._session.commit()
        return result.rowcount > 0

    async def rotate(self, key_id: int, new_hash: str, owner_id: int) -> bool:
        result = await self._session.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.owner_id == owner_id)
        )
        key = result.scalar_one_or_none()
        if key is None:
            return False
        key.key_hash = new_hash
        await self._session.commit()
        return True

