from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.permissions.application.interfaces import CommandPermissionRepository
from app.modules.permissions.application.use_cases import PermissionUseCases
from app.modules.permissions.infrastructure.repositories import SqlAlchemyCommandPermissionRepository


def get_permission_repository(
    session: AsyncSession = Depends(get_session),
) -> CommandPermissionRepository:
    return SqlAlchemyCommandPermissionRepository(session)


def get_permission_use_cases(
    repository: CommandPermissionRepository = Depends(get_permission_repository),
) -> PermissionUseCases:
    return PermissionUseCases(repository)

