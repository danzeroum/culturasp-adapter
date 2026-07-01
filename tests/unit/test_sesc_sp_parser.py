"""Tests for the EXPERIMENTAL SESC São Paulo (children's) parser.

As with the Pinacoteca parser, we assert only what is safe without a verified
real fixture: host matching, that it stays out of the live ``PARSERS`` registry,
the no-title failure path, and the wiring of the children's-specific fields
(schema type, audience, age band) against ILLUSTRATIVE HTML. The production
selectors are validated separately against a real snapshot captured with
``scripts/capture_fixture.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from culturasp.core.exceptions import ParseError
from culturasp.scraper.parsers import ALL_PARSERS, EXPERIMENTAL_PARSERS, PARSERS
from culturasp.scraper.parsers.sesc_sp import SescSPParser

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def test_can_parse_host() -> None:
    parser = SescSPParser()
    assert parser.can_parse("https://www.sescsp.org.br/programacao/foo")
    assert not parser.can_parse("https://salasaopaulo.art.br/x")


def test_stays_experimental_not_live() -> None:
    assert "sesc-sp" not in PARSERS
    assert "sesc-sp" in EXPERIMENTAL_PARSERS
    assert "sesc-sp" in ALL_PARSERS


def test_list_event_urls_discovers_event_paths_only() -> None:
    listing = (
        "<html><body>"
        '<a href="/programacao/o-pequeno-principe">evento</a>'
        '<a href="https://www.sescsp.org.br/programacao/contacao-de-historias/">evento 2</a>'
        '<a href="/programacao/">listagem</a>'
        '<a href="/programacao/feed/">feed</a>'
        '<a href="/programacao/infantil/">categoria</a>'
        '<a href="/unidades/pompeia/">unidade</a>'
        "</body></html>"
    )
    urls = SescSPParser().list_event_urls(listing, "https://www.sescsp.org.br/programacao/")
    assert urls == [
        "https://www.sescsp.org.br/programacao/o-pequeno-principe",
        "https://www.sescsp.org.br/programacao/contacao-de-historias/",
    ]


def test_missing_title_raises() -> None:
    with pytest.raises(ParseError):
        SescSPParser().parse_event(
            "<html><body><p>sem titulo</p></body></html>",
            "https://www.sescsp.org.br/programacao/x",
            scraped_at=NOW,
        )


def test_childrens_event_fields_wired() -> None:
    # ILLUSTRATIVE HTML — the labels here are among the candidates the parser
    # checks; the real site's exact wording is still "A CONFIRMAR". This verifies
    # the children's field wiring (schema type, audience, age band, unit), not the
    # production selectors.
    html = (
        "<html><body>"
        "<h1>O Pequeno Príncipe</h1>"
        "<p><strong>Unidade:</strong> Pompeia</p>"
        "<p><strong>Data:</strong> 8 de agosto de 2026</p>"
        "<p><strong>Horário:</strong> 15:00</p>"
        "<p><strong>Classificação:</strong> a partir de 4 anos</p>"
        "<p><strong>Linguagem:</strong> Teatro</p>"
        "<p>Entrada gratuita.</p>"
        "</body></html>"
    )
    event = SescSPParser().parse_event(
        html, "https://www.sescsp.org.br/programacao/o-pequeno-principe", scraped_at=NOW
    )
    assert event.schema_type.value == "ChildrensEvent"
    assert event.audience == "infantil"
    assert (event.min_age, event.max_age) == (4, None)
    assert event.age_range_text == "4-"
    assert event.category == "Teatro"
    assert event.venue == "Pompeia"
    assert event.start is not None and (event.start.month, event.start.day) == (8, 8)
    assert event.start.hour == 15
    assert event.ticket.free_of_charge is True


def test_free_rating_sets_livre_audience() -> None:
    html = (
        "<html><body>"
        "<h1>Contação de Histórias</h1>"
        "<p><strong>Classificação:</strong> Livre</p>"
        "</body></html>"
    )
    event = SescSPParser().parse_event(
        html, "https://www.sescsp.org.br/programacao/contacao", scraped_at=NOW
    )
    assert event.audience == "livre"
    assert event.min_age == 0 and event.max_age is None
    assert event.age_range_text == "livre"
