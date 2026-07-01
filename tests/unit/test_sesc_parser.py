"""Unit tests for the Sesc parser — fully offline against a JSON fixture."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from culturasp.core.config import Settings
from culturasp.models.event import SchemaType
from culturasp.scraper.parsers import PARSERS
from culturasp.scraper.parsers.sesc import SescParser, cards_to_events

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)
BASE = "https://www.sescsp.org.br"
# The capital slugs present in the fixture (consolacao, belenzinho, pinheiros).
CAPITAL = {"consolacao", "belenzinho", "pinheiros"}


@pytest.fixture
def parser() -> SescParser:
    return SescParser(
        settings=Settings(
            sesc_base_url=BASE,
            sesc_capital_units=",".join(sorted(CAPITAL)),
            sesc_interval="",
        )
    )


class FakeFetcher:
    """Returns canned JSON payloads keyed by page number; records the URLs hit."""

    def __init__(self, pages: dict[int, dict[str, Any]]) -> None:
        self._pages = pages
        self.urls: list[str] = []

    async def fetch_json(self, url: str, *, use_cache: bool = True) -> Any:
        self.urls.append(url)
        page = int(url.split("page=")[1].split("&")[0])
        return self._pages.get(page, {"atividade": []})


def test_registered_as_live_source() -> None:
    assert "sesc" in PARSERS
    assert isinstance(PARSERS["sesc"], SescParser)


def test_can_parse(parser: SescParser) -> None:
    assert parser.can_parse("https://www.sescsp.org.br/programacao/leoni-7")
    assert not parser.can_parse("https://salasaopaulo.art.br/x/concerto/1")


def test_capital_filter_keeps_only_capital_and_skips_cancelled(
    sesc_filter_payload: dict[str, Any],
) -> None:
    events = cards_to_events(
        sesc_filter_payload["atividade"],
        base_url=BASE,
        capital_units=CAPITAL,
        scraped_at=NOW,
    )
    # Consolação + Belenzinho + multi-unit (Franca+Pinheiros); Franca-only and
    # the cancelled activity are dropped.
    assert [e.id for e in events] == ["sesc:1219120", "sesc:900001", "sesc:900003"]


def test_field_mapping(sesc_filter_payload: dict[str, Any]) -> None:
    events = cards_to_events(
        sesc_filter_payload["atividade"], base_url=BASE, capital_units=CAPITAL, scraped_at=NOW
    )
    by_id = {e.id: e for e in events}

    show = by_id["sesc:1219120"]
    assert show.source == "sesc"
    assert str(show.source_url) == "https://www.sescsp.org.br/programacao/fabio-peron-e-lucas-rocha"
    assert show.title == "Fábio Peron e Lucas Rocha"
    assert show.venue == "Sesc Consolação"
    assert show.schema_type is SchemaType.music_event
    assert show.ticket.free_of_charge is False
    # dataProxSessao, made São Paulo-local (UTC-3).
    assert show.start is not None
    assert (show.start.year, show.start.month, show.start.day) == (2026, 7, 7)
    assert show.start.hour == 19
    assert show.start.utcoffset() == timedelta(hours=-3)

    workshop = by_id["sesc:900001"]
    assert workshop.venue == "Sesc Belenzinho"
    assert workshop.schema_type is SchemaType.event  # cursos e oficinas → generic
    assert workshop.ticket.free_of_charge is True
    assert workshop.start is not None and workshop.start.hour == 14  # dataProxSessao, not first


def test_multi_unit_included_when_any_unit_is_capital(
    sesc_filter_payload: dict[str, Any],
) -> None:
    events = cards_to_events(
        sesc_filter_payload["atividade"], base_url=BASE, capital_units=CAPITAL, scraped_at=NOW
    )
    turne = next(e for e in events if e.id == "sesc:900003")
    assert turne.venue == "Sesc Franca"  # first listed unit names the venue


async def test_fetch_events_single_page(
    parser: SescParser, sesc_filter_payload: dict[str, Any]
) -> None:
    fetcher = FakeFetcher({1: sesc_filter_payload})
    events = await parser.fetch_events(fetcher, scraped_at=NOW)
    assert [e.id for e in events] == ["sesc:1219120", "sesc:900001", "sesc:900003"]
    assert len(fetcher.urls) == 1  # 5 cards < page size → no second request
    assert "/wp-json/wp/v1/atividades/filter?ppp=1000&page=1" in fetcher.urls[0]


async def test_fetch_events_respects_max(
    parser: SescParser, sesc_filter_payload: dict[str, Any]
) -> None:
    fetcher = FakeFetcher({1: sesc_filter_payload})
    events = await parser.fetch_events(fetcher, scraped_at=NOW, max_events=1)
    assert [e.id for e in events] == ["sesc:1219120"]


async def test_fetch_events_paginates_and_dedups(
    parser: SescParser, sesc_filter_payload: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force a tiny page size so the fixture spans multiple pages; repeat one
    # capital card across pages to prove de-duplication.
    monkeypatch.setattr("culturasp.scraper.parsers.sesc._PAGE_SIZE", 2)
    cards = sesc_filter_payload["atividade"]
    consolacao, belenzinho, turne = cards[0], cards[1], cards[4]
    # Full pages (len == page size) keep the loop going; a short page ends it.
    page1 = {"atividade": [consolacao, belenzinho]}  # both capital
    page2 = {"atividade": [consolacao, turne]}  # consolacao repeated + multi-unit
    fetcher = FakeFetcher({1: page1, 2: page2})  # page 3 → empty → stop
    events = await parser.fetch_events(fetcher, scraped_at=NOW)
    assert [e.id for e in events] == ["sesc:1219120", "sesc:900001", "sesc:900003"]
    assert len(fetcher.urls) == 3  # two full pages + one empty terminating page


def test_interval_appended_to_url() -> None:
    parser = SescParser(
        settings=Settings(sesc_base_url=BASE, sesc_capital_units="pinheiros", sesc_interval="mes")
    )
    url = parser._page_url(BASE, 1)
    assert url.endswith("?ppp=1000&page=1&intervalo=mes")


def _child_card() -> dict[str, Any]:
    return {
        "id": 101,
        "titulo": "A Força do Amor - Alonso e Marina",
        "link": "/programacao/a-forca-do-amor",
        "unidade": [{"name": "Pinheiros", "link": "/unidades/pinheiros"}],
        "publico_tag": [{"link": "/publico_tag/criancas", "titulo": "Crianças"}],
        "tipos_linguagens": [
            {"titulo": "Shows, Espetáculos e Performances", "children": [{"titulo": "Teatro"}]}
        ],
        "dataProxSessao": "2026-07-11T15:00",
        "gratuito": "Atividade gratuita",
    }


def test_audience_infantil_from_publico_tag() -> None:
    (event,) = cards_to_events(
        [_child_card()], base_url=BASE, capital_units={"pinheiros"}, scraped_at=NOW
    )
    assert event.audience == "infantil"
    # A children's activity is typed as schema.org/ChildrensEvent...
    assert event.schema_type is SchemaType.childrens_event
    # ...and the category prefers the specific leaf ("Teatro") over its parent.
    assert event.category == "Teatro"


def test_audience_livre_from_diversas_idades() -> None:
    card = _child_card()
    card["publico_tag"] = [{"link": "/publico_tag/diversas-idades", "titulo": "Diversas idades"}]
    (event,) = cards_to_events([card], base_url=BASE, capital_units={"pinheiros"}, scraped_at=NOW)
    assert event.audience == "livre"
    # Not children → falls back to the linguagem-based type (Teatro → TheaterEvent).
    assert event.schema_type is SchemaType.theater_event


def test_audience_none_when_no_publico_tag(sesc_filter_payload: dict[str, Any]) -> None:
    events = cards_to_events(
        sesc_filter_payload["atividade"], base_url=BASE, capital_units=CAPITAL, scraped_at=NOW
    )
    # The fixture cards carry no publico_tag, so audience stays unset.
    assert all(e.audience is None for e in events)
