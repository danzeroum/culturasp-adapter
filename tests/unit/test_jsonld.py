"""Unit tests for the JSON-LD (schema.org/MusicEvent) mapper."""

from __future__ import annotations

from datetime import datetime, timezone

from culturasp.models.accessibility import AccessibilityInfo
from culturasp.models.event import CulturalEvent, ProgramItem, SchemaType, TicketPolicy
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


def test_jsonld_exhibition_event_omits_music_props() -> None:
    # A non-music event maps to ExhibitionEvent and drops music-only properties,
    # even if program/conductor happen to be populated.
    event = _sample().model_copy(update={"schema_type": SchemaType.exhibition_event})
    doc = event_to_jsonld(event)
    assert doc["@type"] == "ExhibitionEvent"
    assert doc["location"]["@type"] == "Place"
    assert "workPerformed" not in doc
    assert "performer" not in doc
    # Common properties still present.
    assert doc["name"] == "Orquestra Antares"
    assert doc["isAccessibleForFree"] is True


def test_jsonld_generic_event_type() -> None:
    event = _sample().model_copy(update={"schema_type": SchemaType.event})
    doc = event_to_jsonld(event)
    assert doc["@type"] == "Event"
    assert doc["location"]["@type"] == "Place"
