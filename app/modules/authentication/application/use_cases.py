import secrets

from app.core.security import hash_api_key, verify_password
from app.modules.authentication.application.exceptions import (
    ApiKeyNotFoundError,
    InvalidCredentialsError,
)
from app.modules.authentication.application.interfaces import (
    ApiKeyRepository,
    UserRepository,
)
from app.modules.authentication.domain.entities import ApiKeyEntity, UserEntity


class AuthenticationUseCases:
    def __init__(self, users: UserRepository, keys: ApiKeyRepository) -> None:
        self._users = users
        self._keys = keys

    async def authenticate(self, username: str, password: str) -> UserEntity:
        user = await self._users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return user

    async def issue_api_key(self, owner_id: int, name: str) -> tuple[ApiKeyEntity, str]:
        raw = secrets.token_urlsafe(32)
        entity = await self._keys.create(name, hash_api_key(raw), owner_id)
        return entity, raw

    async def issue_api_key_for_username(
        self, username: str, name: str
    ) -> tuple[ApiKeyEntity, str]:
        user = await self._users.get_by_username(username)
        if user is None:
            raise InvalidCredentialsError()
        return await self.issue_api_key(user.id, name)

    async def list_api_keys_for_username(self, username: str) -> list[ApiKeyEntity]:
        user = await self._users.get_by_username(username)
        if user is None:
            raise InvalidCredentialsError()
        return await self._keys.list_for_user(user.id)

    async def revoke_api_key_for_username(
        self, username: str, key_id: int
    ) -> bool:
        user = await self._users.get_by_username(username)
        if user is None:
            raise InvalidCredentialsError()
        return await self._keys.delete(key_id, user.id)

    async def rotate_api_key_for_username(
        self, username: str, key_id: int
    ) -> tuple[ApiKeyEntity, str]:
        user = await self._users.get_by_username(username)
        if user is None:
            raise InvalidCredentialsError()
        raw = secrets.token_urlsafe(32)
        updated = await self._keys.rotate(key_id, hash_api_key(raw), user.id)
        if not updated:
            raise ApiKeyNotFoundError()
        entity = await self._keys.get_by_hash(hash_api_key(raw))
        if entity is None:
            raise ApiKeyNotFoundError()
        return entity, raw

