from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.content.application.interfaces import ContentRepository
from app.modules.content.application.use_cases import ContentUseCases
from app.modules.content.infrastructure.repositories import SqlAlchemyContentRepository


def get_content_repository(
    session: AsyncSession = Depends(get_session),
) -> ContentRepository:
    return SqlAlchemyContentRepository(session)


def get_content_use_cases(
    repository: ContentRepository = Depends(get_content_repository),
) -> ContentUseCases:
    return ContentUseCases(repository)

