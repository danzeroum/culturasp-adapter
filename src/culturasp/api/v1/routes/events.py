"""/v1/events — list, detail, JSON-LD and iCal/RSS feeds."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from culturasp.api.deps import get_event_repository
from culturasp.api.feeds import events_to_ical, events_to_rss
from culturasp.db.repository import EventRepository
from culturasp.models.event import CulturalEvent
from culturasp.models.jsonld import event_to_jsonld

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[CulturalEvent])
def list_events(
    repo: EventRepository = Depends(get_event_repository),
    source: str | None = Query(None, description="Filter by source slug, e.g. 'sala-sp'"),
    date_from: datetime | None = Query(None, description="Only events starting at/after this"),
    date_to: datetime | None = Query(None, description="Only events starting at/before this"),
    accessible: bool | None = Query(None, description="Filter by any accessibility feature"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[CulturalEvent]:
    return repo.list(
        source=source,
        date_from=date_from,
        date_to=date_to,
        accessible=accessible,
        limit=limit,
        offset=offset,
    )


@router.get(".ics")
def events_ical(repo: EventRepository = Depends(get_event_repository)) -> Response:
    events = repo.list(limit=200)
    return Response(content=events_to_ical(events), media_type="text/calendar")


@router.get(".rss")
def events_rss(repo: EventRepository = Depends(get_event_repository)) -> Response:
    events = repo.list(limit=200)
    return Response(content=events_to_rss(events), media_type="application/rss+xml")


@router.get("/{event_id}", response_model=CulturalEvent)
def get_event(
    event_id: str, repo: EventRepository = Depends(get_event_repository)
) -> CulturalEvent:
    event = repo.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/jsonld")
def get_event_jsonld(event_id: str, repo: EventRepository = Depends(get_event_repository)) -> dict:
    event = repo.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_to_jsonld(event)
