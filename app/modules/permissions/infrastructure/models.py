from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CommandPermission(Base):
    __tablename__ = "command_permissions"

    command: Mapped[str] = mapped_column(String(255), primary_key=True)
    roles: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False)

