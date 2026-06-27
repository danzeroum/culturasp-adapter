"""initial schema: events + source_state

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-27
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accessible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_source", "events", ["source"])
    op.create_index("ix_events_start", "events", ["start"])
    op.create_index("ix_events_accessible", "events", ["accessible"])

    op.create_table(
        "source_state",
        sa.Column("source", sa.String(), primary_key=True),
        sa.Column("layout_signature", sa.Text(), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("source_state")
    op.drop_index("ix_events_accessible", table_name="events")
    op.drop_index("ix_events_start", table_name="events")
    op.drop_index("ix_events_source", table_name="events")
    op.drop_table("events")
