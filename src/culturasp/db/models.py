"""SQLAlchemy ORM models.

Two tables:
  * ``events``  — the latest normalised snapshot of each event (JSON payload +
    a few indexed columns for filtering),
  * ``source_state`` — per-source bookkeeping (last layout signature, last run).

History/auditing can be added later as an append-only ``event_snapshots`` table;
keeping the current snapshot in ``events`` keeps the API read path simple.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    accessible: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # Denormalised audience columns so the API can filter by age/audience without
    # scanning the JSON payload. Derived from CulturalEvent on upsert.
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    max_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    audience: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON)  # full CulturalEvent.model_dump(mode="json")
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SourceState(Base):
    __tablename__ = "source_state"

    source: Mapped[str] = mapped_column(String, primary_key=True)
    layout_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
