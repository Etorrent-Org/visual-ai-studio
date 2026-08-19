"""Schéma local initial Visual AI Studio.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("collection_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("collection_is_new", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("style", sa.Text(), nullable=False, server_default=""),
        sa.Column("brief_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("prompt_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("prompt_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("prompt_brief_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.Column("notion_page_url", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_updated_at", "projects", ["updated_at"])
    op.create_table(
        "reference_values",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("is_new", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sync_status", sa.String(32), nullable=False, server_default="synced"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("type", "normalized_value", name="uq_reference_type_normalized"),
    )
    op.create_index("ix_reference_values_type", "reference_values", ["type"])
    op.create_index(
        "ix_reference_values_normalized_value", "reference_values", ["normalized_value"]
    )
    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("artifact_type", sa.String(32), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("local_path", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("validation_status", sa.String(32), nullable=False),
    )
    op.create_index("ix_artifacts_project_id", "artifacts", ["project_id"])
    op.create_table(
        "n8n_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("request_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("response_at", sa.DateTime(timezone=True)),
        sa.Column("http_status", sa.Integer()),
        sa.Column("execution_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("notion_page_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_n8n_runs_project_id", "n8n_runs", ["project_id"])
    op.create_index("ix_n8n_runs_idempotency_key", "n8n_runs", ["idempotency_key"])


def downgrade() -> None:
    op.drop_table("n8n_runs")
    op.drop_table("artifacts")
    op.drop_table("reference_values")
    op.drop_table("projects")

