"""Unit tests for the iCal and RSS feed rendering."""

from __future__ import annotations

from datetime import datetime, timezone

from culturasp.api.feeds import events_to_ical, events_to_rss
from culturasp.models.event import CulturalEvent, ProgramItem, TicketPolicy

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def _event(**overrides: object) -> CulturalEvent:
    base = {
        "id": "sala-sp:1727",
        "source": "sala-sp",
        "source_url": "https://salasaopaulo.art.br/salasp/pt/concerto/1727",
        "title": "Orquestra Antares",
        "start": datetime(2026, 8, 8, 10, 50, tzinfo=timezone.utc),
        "end": datetime(2026, 8, 8, 11, 50, tzinfo=timezone.utc),
        "conductor": "Fábio Prado",
        "program": [ProgramItem(composer="Mozart", work="Sinfonia nº 40")],
        "ticket": TicketPolicy(free_of_charge=True),
        "scraped_at": NOW,
    }
    base.update(overrides)
    return CulturalEvent(**base)  # type: ignore[arg-type]


def test_ical_contains_event() -> None:
    ics = events_to_ical([_event()])
    assert "BEGIN:VCALENDAR" in ics
    assert "Orquestra Antares" in ics
    assert "Fábio Prado" in ics


def test_ical_minimal_event_without_end_or_program() -> None:
    # Exercises the "no description" + "no end" branches.
    ics = events_to_ical([_event(end=None, conductor=None, program=[])])
    assert "BEGIN:VEVENT" in ics
    assert "Orquestra Antares" in ics


def test_rss_returns_bytes_with_channel_and_item() -> None:
    rss = events_to_rss([_event()])
    assert isinstance(rss, bytes)
    body = rss.decode("utf-8")
    assert "CulturaSP-Adapter" in body
    assert "Orquestra Antares" in body


def test_rss_handles_event_without_start() -> None:
    rss = events_to_rss([_event(start=None, end=None)]).decode("utf-8")
    assert "data a confirmar" in rss
