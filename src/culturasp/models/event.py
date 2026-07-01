"""Core domain models for a cultural event.

These Pydantic models are the canonical representation produced by every parser
and served by the API. They are deliberately source-agnostic: a parser's job is
to map raw HTML/PDF into these shapes.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, model_validator

from culturasp.models.accessibility import AccessibilityInfo


class OCRStatus(str, Enum):
    """Outcome of attempting OCR on an attached PDF (seat map / programme)."""

    not_attempted = "not_attempted"
    success = "success"
    failed = "failed"


class SchemaType(str, Enum):
    """schema.org event type a source maps to (drives the JSON-LD ``@type``).

    Concert halls use ``MusicEvent``; museums/exhibitions use ``ExhibitionEvent``;
    children's theatre/workshops use ``TheaterEvent``/``ChildrensEvent``; anything
    else falls back to the generic ``Event``.
    """

    music_event = "MusicEvent"
    exhibition_event = "ExhibitionEvent"
    theater_event = "TheaterEvent"
    childrens_event = "ChildrensEvent"
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

    # Audience / suitability — populated for family & children's programming.
    # ``min_age``/``max_age`` are the recommended age band (e.g. "a partir de 4
    # anos" → min=4, max=None; "4 a 10 anos" → 4/10; "livre" → min=0). ``audience``
    # is the published label ("infantil", "livre", "família"); ``category`` is the
    # kind of activity ("teatro", "oficina", "contação de histórias", ...).
    min_age: int | None = Field(None, ge=0, description="Recommended minimum age, if published")
    max_age: int | None = Field(None, ge=0, description="Recommended maximum age, if published")
    audience: str | None = Field(None, description="Audience label, e.g. 'infantil' / 'livre'")
    category: str | None = Field(None, description="Activity kind, e.g. 'teatro' / 'oficina'")

    accessibility: AccessibilityInfo = Field(default_factory=AccessibilityInfo)
    ticket: TicketPolicy = Field(default_factory=TicketPolicy)

    seat_map_url: HttpUrl | None = Field(None, description="URL of the seat-map PDF, if any")
    seat_map_text: str | None = Field(None, description="OCR-extracted seat-map text, if any")
    ocr_status: OCRStatus = OCRStatus.not_attempted

    scraped_at: datetime = Field(..., description="When this snapshot was collected")

    @model_validator(mode="after")
    def _check_age_band(self) -> CulturalEvent:
        """A published band must be coherent: ``min_age`` cannot exceed ``max_age``."""
        if self.min_age is not None and self.max_age is not None and self.min_age > self.max_age:
            raise ValueError("min_age cannot be greater than max_age")
        return self

    @property
    def age_range_text(self) -> str | None:
        """Human/schema.org ``typicalAgeRange`` string, e.g. '4-10', '4-', 'livre'.

        Returns ``None`` when no age band is known (so JSON-LD omits the property).
        """
        if self.min_age is None and self.max_age is None:
            return None
        if self.max_age is not None:
            return f"{self.min_age or 0}-{self.max_age}"
        if not self.min_age:  # min 0/None with no max → open to everyone
            return "livre"
        return f"{self.min_age}-"
