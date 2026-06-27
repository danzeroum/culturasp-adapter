"""Structured accessibility information.

The source site publishes accessibility data as free-running prose. We turn it
into explicit, queryable fields so consumers (e.g. a PCD-focused app) can filter
on "needs Libras" or "needs audio description" without reading paragraphs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AccessibilityInfo(BaseModel):
    """Accessibility features available for an event."""

    sign_language: bool = Field(False, description="Libras (Brazilian Sign Language) available")
    audio_description: bool = Field(False, description="Audio description available")
    wheelchair_seats: int | None = Field(None, description="Number of wheelchair-adapted seats")
    obese_seats: int | None = Field(None, description="Number of seats adapted for obese patrons")
    notes: str | None = Field(None, description="Original accessibility text, kept verbatim")

    @property
    def has_any(self) -> bool:
        """True if at least one accessibility feature is present."""
        return bool(
            self.sign_language
            or self.audio_description
            or (self.wheelchair_seats or 0) > 0
            or (self.obese_seats or 0) > 0
        )
