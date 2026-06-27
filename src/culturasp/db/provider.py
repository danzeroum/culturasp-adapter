"""Repository provider — single place that wires storage for app + scraper."""

from __future__ import annotations

from functools import lru_cache

from culturasp.db.repository import SqlEventRepository
from culturasp.db.session import get_sessionmaker


@lru_cache
def get_repository() -> SqlEventRepository:
    """Return the Postgres-backed repository (cached singleton)."""
    return SqlEventRepository(get_sessionmaker())
