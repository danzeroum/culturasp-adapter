"""Unit tests for the JSON-LD (schema.org/MusicEvent) mapper."""

from __future__ import annotations

from datetime import datetime, timezone

from culturasp.models.accessibility import AccessibilityInfo
from culturasp.models.event import CulturalEvent, ProgramItem, TicketPolicy
from culturasp.models.jsonld import event_to_jsonld

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def _sample() -> CulturalEvent:
    return CulturalEvent(
        id="sala-sp:1727",
        source="sala-sp",
        source_url="https://salasaopaulo.art.br/salasp/pt/concerto/1727",
        title="Orquestra Antares",
        start=datetime(2026, 8, 8, 10, 50, tzinfo=timezone.utc),
        end=datetime(2026, 8, 8, 11, 50, tzinfo=timezone.utc),
        duration_minutes=60,
        conductor="Fábio Prado",
        program=[ProgramItem(composer="Mozart", work="Sinfonia nº 40")],
        accessibility=AccessibilityInfo(sign_language=True, wheelchair_seats=15),
        ticket=TicketPolicy(free_of_charge=True),
        scraped_at=NOW,
    )


def test_jsonld_shape() -> None:
    doc = event_to_jsonld(_sample())
    assert doc["@context"] == "https://schema.org"
    assert doc["@type"] == "MusicEvent"
    assert doc["name"] == "Orquestra Antares"
    assert doc["duration"] == "PT60M"
    assert doc["location"]["@type"] == "MusicVenue"
    assert doc["isAccessibleForFree"] is True
    assert doc["offers"]["price"] == "0"


def test_jsonld_accessibility_features() -> None:
    doc = event_to_jsonld(_sample())
    assert "signLanguageInterpretation" in doc["accessibilityFeature"]
    assert "wheelchairAccessibleSeating" in doc["accessibilityFeature"]


def test_jsonld_work_performed() -> None:
    doc = event_to_jsonld(_sample())
    works = doc["workPerformed"]
    assert works[0]["name"] == "Sinfonia nº 40"
    assert works[0]["composer"]["name"] == "Mozart"
