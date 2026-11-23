"""bot_flags key-value state

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS bot_flags ("
        "  flag VARCHAR(128) PRIMARY KEY,"
        "  value TEXT NOT NULL DEFAULT ''"
        ")"
    ))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS bot_flags"))

