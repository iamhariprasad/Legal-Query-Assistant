"""Initial schema.

Revision ID: 202607220001
Revises:
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202607220001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    """Return common timestamp columns."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    """Create production schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_documents_external_id", "documents", ["external_id"], unique=True)

    op.create_table(
        "chat_history",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("citations", sa.JSON(), nullable=False),
        sa.Column("refused", sa.Boolean(), nullable=False),
        sa.Column("refusal_reason", sa.String(length=255), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_chat_history_user_id", "chat_history", ["user_id"])

    op.create_table(
        "search_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("pagenum", sa.Integer(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("chat_id", sa.String(length=36), sa.ForeignKey("chat_history.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_chat_id", "feedback", ["chat_id"])

    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("expected_issue", sa.String(length=255), nullable=False),
        sa.Column("expected_citations", sa.JSON(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("refused", sa.Boolean(), nullable=False),
        sa.Column("citation_accuracy", sa.Float(), nullable=False),
        sa.Column("precision", sa.Float(), nullable=False),
        sa.Column("recall", sa.Float(), nullable=False),
        sa.Column("faithfulness", sa.Float(), nullable=False),
        sa.Column("hallucination_rate", sa.Float(), nullable=False),
        sa.Column("context_recall", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "metrics",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_metrics_name", "metrics", ["name"])

    op.create_table(
        "guardrail_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("chat_id", sa.String(length=36), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("trigger", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_guardrail_logs_chat_id", "guardrail_logs", ["chat_id"])

    op.create_table(
        "embeddings_metadata",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("vector_id", sa.String(length=255), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("citation", sa.String(length=500), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
    )
    op.create_index("ix_embeddings_metadata_document_id", "embeddings_metadata", ["document_id"])
    op.create_index("ix_embeddings_metadata_vector_id", "embeddings_metadata", ["vector_id"], unique=True)


def downgrade() -> None:
    """Drop schema in reverse dependency order."""
    op.drop_table("embeddings_metadata")
    op.drop_table("guardrail_logs")
    op.drop_table("metrics")
    op.drop_table("evaluation_results")
    op.drop_table("feedback")
    op.drop_table("search_logs")
    op.drop_table("chat_history")
    op.drop_table("documents")
    op.drop_table("users")

