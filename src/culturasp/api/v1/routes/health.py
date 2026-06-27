"""/health, /metrics and /v1/sources — liveness and operational status."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from culturasp.api.deps import get_event_repository
from culturasp.db.repository import EventRepository
from culturasp.scraper.parsers import PARSERS

router = APIRouter(tags=["ops"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/metrics")
def metrics(repo: EventRepository = Depends(get_event_repository)) -> dict:
    return {"events_total": repo.count(), "sources": list(PARSERS)}


@router.get("/v1/sources")
def sources(repo: EventRepository = Depends(get_event_repository)) -> list[dict]:
    out = []
    for slug in PARSERS:
        out.append(
            {
                "source": slug,
                "layout_signature": repo.get_layout_signature(slug),
            }
        )
    return out
