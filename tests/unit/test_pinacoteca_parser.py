"""Tests for the EXPERIMENTAL Pinacoteca parser.

We assert only what is safe to assert without a verified real fixture: host
matching, that it stays experimental (out of the live ``PARSERS`` registry), and
the no-title failure path. Selector behavior is validated separately against a
real snapshot captured with ``scripts/capture_fixture.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from culturasp.core.exceptions import ParseError
from culturasp.scraper.parsers import ALL_PARSERS, EXPERIMENTAL_PARSERS, PARSERS
from culturasp.scraper.parsers.pinacoteca import PinacotecaParser

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def test_can_parse_host() -> None:
    parser = PinacotecaParser()
    assert parser.can_parse("https://pinacoteca.org.br/exposicao/foo")
    assert not parser.can_parse("https://salasaopaulo.art.br/x")


def test_stays_experimental_not_live() -> None:
    # Must NOT be wired into the live runtime registry...
    assert "pinacoteca" not in PARSERS
    # ...but must be discoverable for tooling/tests.
    assert "pinacoteca" in EXPERIMENTAL_PARSERS
    assert "pinacoteca" in ALL_PARSERS


def test_missing_title_raises() -> None:
    parser = PinacotecaParser()
    with pytest.raises(ParseError):
        parser.parse_event(
            "<html><body><p>sem titulo</p></body></html>",
            "https://pinacoteca.org.br/exposicao/x",
            scraped_at=NOW,
        )


def test_exhibition_period_fills_start_and_end() -> None:
    # ILLUSTRATIVE HTML — the period label here ("Período") is one of the
    # candidates the parser checks; the real site's label is still "A CONFIRMAR".
    # This verifies the date-range wiring, not the production selectors.
    html = (
        "<html><body>"
        "<h1>Exposição Exemplo</h1>"
        "<p><strong>Período:</strong> De 10 de maio a 20 de agosto de 2026</p>"
        "</body></html>"
    )
    event = PinacotecaParser().parse_event(
        html, "https://pinacoteca.org.br/exposicao/exemplo", scraped_at=NOW
    )
    assert event.schema_type.value == "ExhibitionEvent"
    assert event.start is not None and (event.start.month, event.start.day) == (5, 10)
    assert event.end is not None and (event.end.month, event.end.day) == (8, 20)
