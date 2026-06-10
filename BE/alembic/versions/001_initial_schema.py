"""Initial database schema with pgvector support.

Revision ID: 001_initial
Revises:
Create Date: 2026-06-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSION = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "sources",
        sa.Column("guid", sa.UUID(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("guid"),
        sa.UniqueConstraint("url"),
    )

    op.create_table(
        "news_chunks",
        sa.Column("guid", sa.UUID(), nullable=False),
        sa.Column("source_guid", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSION), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_guid"],
            ["sources.guid"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("guid"),
    )

    op.create_index(
        "news_chunks_source_guid_idx",
        "news_chunks",
        ["source_guid"],
    )

    op.execute(
        """
        CREATE UNIQUE INDEX news_chunks_text_hash_idx
        ON news_chunks (encode(digest(text, 'sha256'), 'hex'))
        """
    )

    op.execute(
        """
        CREATE INDEX news_chunks_embedding_idx
        ON news_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS news_chunks_embedding_idx")
    op.execute("DROP INDEX IF EXISTS news_chunks_text_hash_idx")
    op.drop_index("news_chunks_source_guid_idx", table_name="news_chunks")
    op.drop_table("news_chunks")
    op.drop_table("sources")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
