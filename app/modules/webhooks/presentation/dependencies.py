from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.webhooks.application.interfaces import WebhookRepository
from app.modules.webhooks.application.use_cases import WebhookUseCases
from app.modules.webhooks.infrastructure.repositories import SqlAlchemyWebhookRepository


def get_webhook_repository(
    session: AsyncSession = Depends(get_session),
) -> WebhookRepository:
    return SqlAlchemyWebhookRepository(session)


def get_webhook_use_cases(
    repository: WebhookRepository = Depends(get_webhook_repository),
) -> WebhookUseCases:
    return WebhookUseCases(repository)

