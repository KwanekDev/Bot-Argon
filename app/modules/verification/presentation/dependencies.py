from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.verification.application.interfaces import (
    RobloxProfileClient,
    VerificationRepository,
)
from app.modules.verification.application.use_cases import VerificationUseCases
from app.modules.verification.infrastructure.roblox_client import RobloxProfileClient as HttpRobloxProfileClient
from app.modules.verification.infrastructure.repositories import SqlAlchemyVerificationRepository


def get_verification_repository(
    session: AsyncSession = Depends(get_session),
) -> VerificationRepository:
    return SqlAlchemyVerificationRepository(session)


def get_roblox_profile_client() -> RobloxProfileClient:
    return HttpRobloxProfileClient()


def get_verification_use_cases(
    repository: VerificationRepository = Depends(get_verification_repository),
    client: RobloxProfileClient = Depends(get_roblox_profile_client),
) -> VerificationUseCases:
    return VerificationUseCases(repository, client)

