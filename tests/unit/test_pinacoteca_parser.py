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
