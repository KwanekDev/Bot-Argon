"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent DDL: tolerates pre-existing tables created by the legacy schema.sql.
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS users ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  username VARCHAR(64) NOT NULL UNIQUE,"
        "  password_hash VARCHAR(255) NOT NULL,"
        "  role VARCHAR(16) NOT NULL DEFAULT 'user',"
        "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS api_keys ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name VARCHAR(128) NOT NULL,"
        "  key_hash VARCHAR(64) NOT NULL UNIQUE,"
        "  owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
        "  scopes VARCHAR(64) NOT NULL DEFAULT 'read',"
        "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ")"
    ))
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS warns ("
        "  id INTEGER PRIMARY KEY,"
        "  user_id VARCHAR(20) NOT NULL,"
        "  server_id VARCHAR(20) NOT NULL,"
        "  moderator_id VARCHAR(20) NOT NULL,"
        "  reason VARCHAR(255) NOT NULL,"
        "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ")"
    ))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS warns"))
    op.execute(sa.text("DROP TABLE IF EXISTS api_keys"))
    op.execute(sa.text("DROP TABLE IF EXISTS users"))

