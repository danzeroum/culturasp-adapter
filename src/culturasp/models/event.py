"""Core domain models for a cultural event.

These Pydantic models are the canonical representation produced by every parser
and served by the API. They are deliberately source-agnostic: a parser's job is
to map raw HTML/PDF into these shapes.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from culturasp.models.accessibility import AccessibilityInfo


class OCRStatus(str, Enum):
    """Outcome of attempting OCR on an attached PDF (seat map / programme)."""

    not_attempted = "not_attempted"
    success = "success"
    failed = "failed"


class SchemaType(str, Enum):
    """schema.org event type a source maps to (drives the JSON-LD ``@type``).

    Concert halls use ``MusicEvent``; museums/exhibitions use ``ExhibitionEvent``;
    anything else falls back to the generic ``Event``.
    """

    music_event = "MusicEvent"
    exhibition_event = "ExhibitionEvent"
    event = "Event"


class ProgramItem(BaseModel):
    """A single piece in the concert programme."""

    composer: str | None = Field(None, description="Composer name")
    work: str | None = Field(None, description="Title of the work performed")


class TicketPolicy(BaseModel):
    """Ticket distribution / cancellation policy.

    NOTE: this is descriptive only. The adapter never automates reservation or
    cancellation — those windows are surfaced as text and an external link.
    """

    free_of_charge: bool = Field(True, description="Whether tickets are free")
    distribution_window: str | None = Field(
        None, description='When tickets become available, e.g. "T-3 days at 12h" (verbatim text)'
    )
    cancellation_window: str | None = Field(
        None, description="Cancellation deadline as published (verbatim text)"
    )
    external_url: HttpUrl | None = Field(
        None, description="Official ticket page (reference link only — not automated)"
    )


class CulturalEvent(BaseModel):
    """A cultural event normalised from a public source."""

    id: str = Field(..., description="Stable id: '{source}:{source_event_id}'")
    source: str = Field(..., description="Source slug, e.g. 'sala-sp'")
    source_url: HttpUrl = Field(..., description="Canonical public URL of the event")
    title: str

    start: datetime | None = Field(None, description="Start datetime (ISO 8601, local tz)")
    end: datetime | None = Field(None, description="End datetime (ISO 8601, local tz)")
    duration_minutes: int | None = Field(None, description="Duration in minutes, if published")

    schema_type: SchemaType = Field(
        SchemaType.music_event, description="schema.org event type for JSON-LD"
    )
    venue: str = Field("Sala São Paulo", description="Venue name")
    program: list[ProgramItem] = Field(default_factory=list)
    conductor: str | None = None
    performers: list[str] = Field(default_factory=list)

    accessibility: AccessibilityInfo = Field(default_factory=AccessibilityInfo)
    ticket: TicketPolicy = Field(default_factory=TicketPolicy)

    seat_map_url: HttpUrl | None = Field(None, description="URL of the seat-map PDF, if any")
    seat_map_text: str | None = Field(None, description="OCR-extracted seat-map text, if any")
    ocr_status: OCRStatus = OCRStatus.not_attempted

    scraped_at: datetime = Field(..., description="When this snapshot was collected")
