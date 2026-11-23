from typing import Protocol

from app.modules.authentication.domain.entities import ApiKeyEntity, UserEntity


class UserRepository(Protocol):
    async def get_by_username(self, username: str) -> UserEntity | None: ...

    async def create(
        self, username: str, password_hash: str, role: str = "user"
    ) -> UserEntity: ...


class ApiKeyRepository(Protocol):
    async def create(
        self, name: str, key_hash: str, owner_id: int
    ) -> ApiKeyEntity: ...

    async def get_by_hash(self, key_hash: str) -> ApiKeyEntity | None: ...

    async def list_for_user(self, owner_id: int) -> list[ApiKeyEntity]: ...

    async def delete(self, key_id: int, owner_id: int) -> bool: ...

    async def rotate(
        self, key_id: int, new_hash: str, owner_id: int
    ) -> bool: ...

