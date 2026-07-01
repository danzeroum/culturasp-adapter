"""Unit tests for the Sala São Paulo parser — fully offline against fixtures."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from culturasp.core.exceptions import ParseError
from culturasp.models.event import OCRStatus
from culturasp.scraper.cli import LISTING_PATHS
from culturasp.scraper.parsers.sala_sp import SalaSPParser

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def test_listing_path_is_full_programme() -> None:
    # "/programacao" only shows the next few concerts; the ticketing programme
    # page renders the whole season, so that's what we scrape.
    assert LISTING_PATHS["sala-sp"].endswith("/programacao-ingressos")


@pytest.fixture
def parser() -> SalaSPParser:
    return SalaSPParser()


def test_can_parse(parser: SalaSPParser) -> None:
    assert parser.can_parse("https://salasaopaulo.art.br/salasp/pt/concerto/1727")
    assert not parser.can_parse("https://example.com/event/1")


def test_list_event_urls_discovers_only_concerts(parser: SalaSPParser, listing_html: str) -> None:
    urls = parser.list_event_urls(listing_html, "https://salasaopaulo.art.br")
    assert urls == [
        "https://salasaopaulo.art.br/salasp/pt/concerto/1727",
        "https://salasaopaulo.art.br/salasp/pt/concerto/1801",
    ]


def test_list_event_urls_handles_relative_hrefs(parser: SalaSPParser) -> None:
    # The live listing links are relative ("concerto/1586") and resolve against
    # the listing URL's directory. Non-concert links must be ignored.
    html = """
    <a href="concerto/1586">A</a>
    <a href="concerto/1587?x=1">B</a>
    <a href="/osesp/pt/concertos-ingressos">tickets</a>
    <a href="programacao-ingressos">prog</a>
    """
    base = "https://salasaopaulo.art.br/salasp/pt/programacao"
    assert parser.list_event_urls(html, base) == [
        "https://salasaopaulo.art.br/salasp/pt/concerto/1586",
        "https://salasaopaulo.art.br/salasp/pt/concerto/1587",
    ]


def test_parse_event_skips_empty_leading_h1(parser: SalaSPParser) -> None:
    # Live concert pages have an empty first <h1> before the real title.
    html = "<html><body><h1></h1><h1>Concerto Real</h1></body></html>"
    url = "https://salasaopaulo.art.br/salasp/pt/concerto/1586"
    event = parser.parse_event(html, url, scraped_at=NOW)
    assert event.title == "Concerto Real"
    assert event.id == "sala-sp:1586"


def test_parse_event_resolves_relative_ticket_url(parser: SalaSPParser) -> None:
    # Ticket links are relative on the live site; external_url needs to be absolute.
    html = '<h1>Show</h1><a href="/osesp/pt/informacoes-ingressos">Ingressos</a>'
    url = "https://salasaopaulo.art.br/salasp/pt/concerto/1586"
    event = parser.parse_event(html, url, scraped_at=NOW)
    assert (
        str(event.ticket.external_url)
        == "https://salasaopaulo.art.br/osesp/pt/informacoes-ingressos"
    )


def test_parse_program_splits_uppercase_composers(parser: SalaSPParser) -> None:
    # Live pages put the whole programme in one <p> with UPPERCASE composers,
    # followed by descriptive prose that must be ignored.
    html = (
        "<h1>X</h1>"
        "<h2>Programa</h2>"
        "<p>FELIX MENDELSSOHN-BARTHOLDY Sinfonia nº 4, Op. 90 "
        "WILLIAM WALTON Concerto para viola</p>"
        "<p>Neste programa, afirma Fischer, há conexões escondidas.</p>"
        "<h2>Mais informações</h2>"
    )
    event = parser.parse_event(html, "https://salasaopaulo.art.br/x/concerto/1", scraped_at=NOW)
    assert [(p.composer, p.work) for p in event.program] == [
        ("Felix Mendelssohn-Bartholdy", "Sinfonia nº 4, Op. 90"),
        ("William Walton", "Concerto para viola"),
    ]


def test_parse_event_extracts_conductor_from_prose(parser: SalaSPParser) -> None:
    html = "<h1>X</h1><p>Sob regência de Thierry Fischer, a Osesp apresenta.</p>"
    event = parser.parse_event(html, "https://salasaopaulo.art.br/x/concerto/1", scraped_at=NOW)
    assert event.conductor == "Thierry Fischer"


def test_parse_event_extracts_conductor_from_credit_line(parser: SalaSPParser) -> None:
    # Programme pages credit the conductor as "<Name> regente" (name before the
    # role). An adjacent "Programa" heading must not bleed into the captured name.
    html = (
        "<h1>X</h1><h2>Programa</h2>"
        "<p>Claudia Feres regente Gabriel Brandão piano</p>"
    )
    event = parser.parse_event(html, "https://salasaopaulo.art.br/x/concerto/1", scraped_at=NOW)
    assert event.conductor == "Claudia Feres"


def test_parse_event_core_fields(parser: SalaSPParser, concert_html: str) -> None:
    url = "https://salasaopaulo.art.br/salasp/pt/concerto/1727"
    event = parser.parse_event(concert_html, url, scraped_at=NOW)

    assert event.id == "sala-sp:1727"
    assert event.source == "sala-sp"
    assert event.title == "Orquestra Antares — Matinais"
    assert event.venue == "Sala São Paulo"
    assert event.conductor == "Fábio Prado"
    assert event.duration_minutes == 60
    assert event.start is not None
    assert (event.start.year, event.start.month, event.start.day) == (2026, 8, 8)
    assert (event.start.hour, event.start.minute) == (10, 50)
    assert event.end is not None and event.end.hour == 11 and event.end.minute == 50


def test_parse_program(parser: SalaSPParser, concert_html: str) -> None:
    event = parser.parse_event(
        concert_html, "https://salasaopaulo.art.br/x/concerto/1727", scraped_at=NOW
    )
    composers = [p.composer for p in event.program]
    assert "Antonio Carlos Gomes" in composers
    assert any("Mozart" in (c or "") for c in composers)
    assert len(event.program) == 3


def test_parse_accessibility(parser: SalaSPParser, concert_html: str) -> None:
    event = parser.parse_event(
        concert_html, "https://salasaopaulo.art.br/x/concerto/1727", scraped_at=NOW
    )
    acc = event.accessibility
    assert acc.sign_language is True
    assert acc.audio_description is True
    assert acc.wheelchair_seats == 15
    assert acc.obese_seats == 14
    assert acc.has_any is True


def test_parse_ticket_and_seatmap(parser: SalaSPParser, concert_html: str) -> None:
    event = parser.parse_event(
        concert_html, "https://salasaopaulo.art.br/x/concerto/1727", scraped_at=NOW
    )
    assert event.ticket.free_of_charge is True
    assert event.ticket.cancellation_window == "até 48h antes do concerto"
    assert str(event.ticket.external_url).startswith("https://ingressos.salasaopaulo.art.br")
    assert event.seat_map_url is not None
    assert str(event.seat_map_url).endswith("mapa-assentos-1727.pdf")
    assert event.ocr_status is OCRStatus.not_attempted


def test_missing_title_raises(parser: SalaSPParser) -> None:
    with pytest.raises(ParseError):
        parser.parse_event(
            "<html><body><p>no title</p></body></html>",
            "https://salasaopaulo.art.br/x",
            scraped_at=NOW,
        )
