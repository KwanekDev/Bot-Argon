"""verification, content templates, webhooks, command permissions

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS content_templates ("
        "  key VARCHAR(128) PRIMARY KEY,"
        "  payload TEXT NOT NULL"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS webhooks ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name VARCHAR(128) NOT NULL UNIQUE,"
        "  url TEXT NOT NULL,"
        "  color INTEGER NOT NULL DEFAULT 0,"
        "  enabled INTEGER NOT NULL DEFAULT 1"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS command_permissions ("
        "  command VARCHAR(255) PRIMARY KEY,"
        "  roles TEXT NOT NULL DEFAULT '[]',"
        "  permissions TEXT NOT NULL DEFAULT '[]'"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS roblox_links ("
        "  discord_id VARCHAR(32) PRIMARY KEY,"
        "  roblox_id VARCHAR(32) NOT NULL UNIQUE,"
        "  verified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS verification_pending ("
        "  discord_id VARCHAR(32) PRIMARY KEY,"
        "  code VARCHAR(16) NOT NULL,"
        "  roblox_id VARCHAR(32) NOT NULL,"
        "  expires_at TIMESTAMP NOT NULL"
        ")"
    ))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS verification_pending"))
    op.execute(sa.text("DROP TABLE IF EXISTS roblox_links"))
    op.execute(sa.text("DROP TABLE IF EXISTS command_permissions"))
    op.execute(sa.text("DROP TABLE IF EXISTS webhooks"))
    op.execute(sa.text("DROP TABLE IF EXISTS content_templates"))

