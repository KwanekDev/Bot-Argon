from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RobloxLink(Base):
    __tablename__ = "roblox_links"

    discord_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    roblox_id: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class PendingVerification(Base):
    __tablename__ = "verification_pending"

    discord_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    roblox_id: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

