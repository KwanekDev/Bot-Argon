from typing import Any

from sqlalchemy import JSON, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StrefaCommand(Base):
    __tablename__ = "strefa_commands"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    options: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    devonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    testonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permissions_required: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    bot_permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    send_to: Mapped[str] = mapped_column(String(64), nullable=False)
    whitelisted_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    roles_to_give: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)


class EventTemplate(Base):
    __tablename__ = "event_templates"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

