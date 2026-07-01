"""Event repositories.

A small abstraction over storage so the API and pipeline don't depend on
SQLAlchemy directly. ``InMemoryEventRepository`` keeps tests fast and offline;
``SqlEventRepository`` is the Postgres-backed production implementation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from culturasp.db.models import EventRow, SourceState
from culturasp.models.event import CulturalEvent


class EventRepository(Protocol):
    def upsert(self, event: CulturalEvent) -> None: ...

    def get(self, event_id: str) -> CulturalEvent | None: ...

    def list(
        self,
        *,
        source: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        accessible: bool | None = None,
        audience: str | None = None,
        age: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CulturalEvent]: ...

    def count(self) -> int: ...

    def get_layout_signature(self, source: str) -> str | None: ...

    def set_layout_signature(self, source: str, signature: str) -> None: ...


def _age_matches(event: CulturalEvent, age: int) -> bool:
    """True if ``age`` falls within the event's published age band.

    Events without any age band are excluded — suitability can't be confirmed.
    """
    if event.min_age is None and event.max_age is None:
        return False
    if event.min_age is not None and age < event.min_age:
        return False
    return not (event.max_age is not None and age > event.max_age)


def _matches(
    event: CulturalEvent,
    *,
    source: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
    accessible: bool | None,
    audience: str | None,
    age: int | None,
) -> bool:
    if source and event.source != source:
        return False
    if accessible is not None and event.accessibility.has_any != accessible:
        return False
    if audience and (event.audience or "").lower() != audience.lower():
        return False
    if age is not None and not _age_matches(event, age):
        return False
    if date_from and (event.start is None or event.start < date_from):
        return False
    return not (date_to and (event.start is None or event.start > date_to))


class InMemoryEventRepository:
    """Dict-backed repository — used in tests and for running without Postgres."""

    def __init__(self) -> None:
        self._events: dict[str, CulturalEvent] = {}
        self._signatures: dict[str, str] = {}

    def upsert(self, event: CulturalEvent) -> None:
        self._events[event.id] = event

    def get(self, event_id: str) -> CulturalEvent | None:
        return self._events.get(event_id)

    def list(
        self,
        *,
        source: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        accessible: bool | None = None,
        audience: str | None = None,
        age: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CulturalEvent]:
        items = [
            e
            for e in self._events.values()
            if _matches(
                e,
                source=source,
                date_from=date_from,
                date_to=date_to,
                accessible=accessible,
                audience=audience,
                age=age,
            )
        ]
        items.sort(key=lambda e: (e.start is None, e.start or datetime.max))
        return items[offset : offset + limit]

    def count(self) -> int:
        return len(self._events)

    def get_layout_signature(self, source: str) -> str | None:
        return self._signatures.get(source)

    def set_layout_signature(self, source: str, signature: str) -> None:
        self._signatures[source] = signature


class SqlEventRepository:
    """Postgres-backed repository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def upsert(self, event: CulturalEvent) -> None:
        with self._session_factory() as session:
            row = session.get(EventRow, event.id)
            payload = event.model_dump(mode="json")
            if row is None:
                row = EventRow(id=event.id)
                session.add(row)
            row.source = event.source
            row.title = event.title
            row.start = event.start
            row.accessible = event.accessibility.has_any
            row.min_age = event.min_age
            row.max_age = event.max_age
            row.audience = event.audience
            row.payload = payload
            row.scraped_at = event.scraped_at
            session.commit()

    def get(self, event_id: str) -> CulturalEvent | None:
        with self._session_factory() as session:
            row = session.get(EventRow, event_id)
            return CulturalEvent.model_validate(row.payload) if row else None

    def list(
        self,
        *,
        source: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        accessible: bool | None = None,
        audience: str | None = None,
        age: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CulturalEvent]:
        stmt = select(EventRow)
        if source:
            stmt = stmt.where(EventRow.source == source)
        if accessible is not None:
            stmt = stmt.where(EventRow.accessible == accessible)
        if audience:
            stmt = stmt.where(EventRow.audience == audience)
        if age is not None:
            # Only events with a published band; the band must include ``age``.
            stmt = stmt.where(
                or_(EventRow.min_age.isnot(None), EventRow.max_age.isnot(None)),
                or_(EventRow.min_age.is_(None), EventRow.min_age <= age),
                or_(EventRow.max_age.is_(None), EventRow.max_age >= age),
            )
        if date_from:
            stmt = stmt.where(EventRow.start >= date_from)
        if date_to:
            stmt = stmt.where(EventRow.start <= date_to)
        stmt = stmt.order_by(EventRow.start.asc().nullslast()).limit(limit).offset(offset)
        with self._session_factory() as session:
            rows = session.execute(stmt).scalars().all()
            return [CulturalEvent.model_validate(r.payload) for r in rows]

    def count(self) -> int:
        with self._session_factory() as session:
            return session.query(EventRow).count()

    def get_layout_signature(self, source: str) -> str | None:
        with self._session_factory() as session:
            state = session.get(SourceState, source)
            return state.layout_signature if state else None

    def set_layout_signature(self, source: str, signature: str) -> None:
        with self._session_factory() as session:
            state = session.get(SourceState, source)
            if state is None:
                state = SourceState(source=source)
                session.add(state)
            state.layout_signature = signature
            session.commit()
