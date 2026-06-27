"""/v1/accessibility — events filtered by an accessibility feature."""

from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, Depends, Query

from culturasp.api.deps import get_event_repository
from culturasp.db.repository import EventRepository
from culturasp.models.event import CulturalEvent

router = APIRouter(prefix="/accessibility", tags=["accessibility"])


class Feature(str, Enum):
    libras = "libras"
    audio_description = "audio_description"
    wheelchair = "wheelchair"


def _has_feature(event: CulturalEvent, feature: Feature) -> bool:
    acc = event.accessibility
    if feature is Feature.libras:
        return acc.sign_language
    if feature is Feature.audio_description:
        return acc.audio_description
    if feature is Feature.wheelchair:
        return (acc.wheelchair_seats or 0) > 0
    return False


@router.get("", response_model=list[CulturalEvent])
def list_accessible_events(
    repo: EventRepository = Depends(get_event_repository),
    feature: Feature | None = Query(None, description="Required accessibility feature"),
    limit: int = Query(50, ge=1, le=200),
) -> list[CulturalEvent]:
    events = repo.list(accessible=True, limit=limit)
    if feature is not None:
        events = [e for e in events if _has_feature(e, feature)]
    return events
