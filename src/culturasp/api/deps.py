"""FastAPI dependencies.

The repository is resolved through a single provider so tests can override it
with an in-memory implementation via ``app.dependency_overrides``.
"""

from __future__ import annotations

from culturasp.db.provider import get_repository
from culturasp.db.repository import EventRepository


def get_event_repository() -> EventRepository:
    return get_repository()
