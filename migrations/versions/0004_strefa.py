"""strefa: commands, applications, event templates

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS strefa_commands ("
        "  name VARCHAR(64) PRIMARY KEY,"
        "  description TEXT NOT NULL DEFAULT '',"
        "  options TEXT NOT NULL DEFAULT '[]',"
        "  devonly INTEGER NOT NULL DEFAULT 0,"
        "  testonly INTEGER NOT NULL DEFAULT 0,"
        "  permissions_required TEXT NOT NULL DEFAULT '[]',"
        "  bot_permissions TEXT NOT NULL DEFAULT '[]',"
        "  deleted INTEGER NOT NULL DEFAULT 0"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS applications ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name TEXT NOT NULL,"
        "  parent_channel TEXT NOT NULL,"
        "  send_to TEXT NOT NULL,"
        "  whitelisted_roles TEXT NOT NULL DEFAULT '[]',"
        "  roles_to_give TEXT NOT NULL DEFAULT '[]',"
        "  questions TEXT NOT NULL DEFAULT '[]'"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS event_templates ("
        "  key VARCHAR(128) PRIMARY KEY,"
        "  payload TEXT NOT NULL"
        ")"
    ))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS event_templates"))
    op.execute(sa.text("DROP TABLE IF EXISTS applications"))
    op.execute(sa.text("DROP TABLE IF EXISTS strefa_commands"))

