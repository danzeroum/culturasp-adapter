"""audience/age columns on events (children's programming)

Revision ID: 0002_children_fields
Revises: 0001_initial
Create Date: 2026-07-01
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_children_fields"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("events", sa.Column("min_age", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("max_age", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("audience", sa.String(), nullable=True))
    op.create_index("ix_events_min_age", "events", ["min_age"])
    op.create_index("ix_events_audience", "events", ["audience"])


def downgrade() -> None:
    op.drop_index("ix_events_audience", table_name="events")
    op.drop_index("ix_events_min_age", table_name="events")
    op.drop_column("events", "audience")
    op.drop_column("events", "max_age")
    op.drop_column("events", "min_age")
