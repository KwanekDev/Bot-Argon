from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.warns.application.interfaces import WarnRepository
from app.modules.warns.application.use_cases import WarnUseCases
from app.modules.warns.infrastructure.repositories import SqlAlchemyWarnRepository


def get_warn_repository(
    session: AsyncSession = Depends(get_session),
) -> WarnRepository:
    return SqlAlchemyWarnRepository(session)


def get_warn_use_cases(
    repository: WarnRepository = Depends(get_warn_repository),
) -> WarnUseCases:
    return WarnUseCases(repository)

