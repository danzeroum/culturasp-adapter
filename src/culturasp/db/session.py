"""Database engine/session factory."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from culturasp.core.config import get_settings
from culturasp.db.models import Base


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session)


def create_all() -> None:
    """Create tables (used for local/dev; production uses Alembic migrations)."""
    Base.metadata.create_all(get_engine())
