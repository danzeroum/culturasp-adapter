"""Parser for the Sesc São Paulo programme.

Unlike Sala São Paulo (rendered HTML + PDFs), Sesc exposes a public WordPress
JSON API — ``GET /wp-json/wp/v1/atividades/filter`` — that returns structured
activity cards for the whole state. This parser is therefore **API-native**: it
builds :class:`CulturalEvent` objects straight from that JSON (via
:meth:`fetch_events`), with no per-event page fetch. Detail pages are a
JavaScript SPA and add nothing the API doesn't already carry.

Scope is limited to units in the **city of São Paulo (the "capital")**. Each
activity's payload lists its unit(s) as ``{"name", "link": "/unidades/<slug>"}``;
we keep an activity when any of its unit slugs is in the configured capital
allowlist (``settings.sesc_capital_unit_set``). The API's own ``local`` filter
needs an opaque unit id that isn't derivable from the payload, so the capital
filter is applied client-side on the slug.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

from culturasp.core.config import Settings, get_settings
from culturasp.core.logging import get_logger
from culturasp.models.event import CulturalEvent, SchemaType, TicketPolicy
from culturasp.scraper.fetcher import Fetcher
from culturasp.scraper.parsers._common import clean_text
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)

# São Paulo is UTC-3 all year (no DST since 2019). The API prints naive local
# datetimes ("2026-07-07T19:00"); we attach this offset to make them tz-aware.
_SP_TZ = timezone(timedelta(hours=-3))

# API endpoint + per-page size. The API caps a page at 1000; we page until the
# reported total is covered.
_FILTER_PATH = "/wp-json/wp/v1/atividades/filter"
_PAGE_SIZE = 1000


def _unit_slugs(card: dict[str, Any]) -> list[str]:
    """Extract unit slugs ("belenzinho") from a card's ``unidade`` list."""
    slugs: list[str] = []
    for unit in card.get("unidade") or []:
        link = (unit.get("link") or "").strip("/")
        if link:
            slugs.append(link.rsplit("/", 1)[-1].lower())
    return slugs


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an API datetime ("2026-07-07T19:00") as São Paulo local time."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=_SP_TZ)
    except ValueError:
        return None


def _schema_type(card: dict[str, Any]) -> SchemaType:
    """Best-effort schema.org type from the activity's ``tipos_linguagens``.

    Sesc is multidisciplinary; only music and exhibitions map to a specific
    schema.org class, everything else stays the generic ``Event``.
    """
    labels: list[str] = []
    for top in card.get("tipos_linguagens") or []:
        labels.append((top.get("titulo") or "").lower())
        for child in top.get("children") or []:
            labels.append((child.get("titulo") or "").lower())
    blob = " ".join(labels)
    if "música" in blob or "musica" in blob:
        return SchemaType.music_event
    if "exposi" in blob:  # exposição / exposições
        return SchemaType.exhibition_event
    if "teatro" in blob:
        return SchemaType.theater_event
    return SchemaType.event


#: Sesc's ``publico_tag`` controlled vocabulary (slug of ``/publico_tag/<slug>``).
_CHILD_TAG_SLUGS = {"criancas", "crianca", "bebes", "bebe", "infantil"}
_OPEN_TAG_SLUGS = {"diversas-idades", "todas-as-idades", "todos-os-publicos", "livre", "familia"}


def _publico_meta(card: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return the ``publico_tag`` (slugs, titles) for an activity card."""
    slugs: list[str] = []
    titles: list[str] = []
    for tag in card.get("publico_tag") or []:
        link = (tag.get("link") or "").strip("/")
        if link:
            slugs.append(link.rsplit("/", 1)[-1].lower())
        title = clean_text(tag.get("titulo"))
        if title:
            titles.append(title)
    return slugs, titles


def _audience_from_card(card: dict[str, Any]) -> str | None:
    """Normalised audience label from the activity's ``publico_tag``.

    Sesc tags the target public with a controlled vocabulary
    (``/publico_tag/<slug>``): children (``criancas``/``bebes``) → "infantil";
    all-ages (``diversas-idades``/...) → "livre"; otherwise the tag's own label.
    Numeric ages are not exposed by this field, so ``min_age``/``max_age`` stay
    ``None`` and children's programming is filtered via ``audience=infantil``.
    """
    slugs, titles = _publico_meta(card)
    if any(s in _CHILD_TAG_SLUGS for s in slugs):
        return "infantil"
    if any(s in _OPEN_TAG_SLUGS for s in slugs):
        return "livre"
    return titles[0].lower() if titles else None


def _category_from_card(card: dict[str, Any]) -> str | None:
    """Most specific activity category from ``tipos_linguagens`` (leaf preferred)."""
    for top in card.get("tipos_linguagens") or []:
        for child in top.get("children") or []:
            label = clean_text(child.get("titulo"))
            if label:
                return label
        label = clean_text(top.get("titulo"))
        if label:
            return label
    return None


def _card_to_event(
    card: dict[str, Any], *, base_url: str, scraped_at: datetime
) -> CulturalEvent | None:
    """Map one API card to a :class:`CulturalEvent` (``None`` if unusable)."""
    title = clean_text(card.get("titulo"))
    link = card.get("link")
    card_id = card.get("id")
    if not title or not link or card_id is None:
        return None

    units = card.get("unidade") or []
    venue = f"Sesc {units[0]['name']}" if units and units[0].get("name") else "Sesc São Paulo"
    source_url = urljoin(base_url, str(link))

    # A children's activity is best typed as schema.org/ChildrensEvent; otherwise
    # fall back to the linguagem-based type (music/exhibition/theater/event).
    audience = _audience_from_card(card)
    schema_type = SchemaType.childrens_event if audience == "infantil" else _schema_type(card)

    return CulturalEvent(
        id=f"sesc:{card_id}",
        source="sesc",
        source_url=source_url,
        title=title,
        schema_type=schema_type,
        audience=audience,
        category=_category_from_card(card),
        # dataProxSessao is the next upcoming session; fall back to the first.
        start=_parse_dt(card.get("dataProxSessao") or card.get("dataPrimeiraSessao")),
        end=None,
        venue=venue,
        ticket=TicketPolicy(
            # "Atividade gratuita" (truthy) vs "" (paid/undisclosed).
            free_of_charge=bool(card.get("gratuito")),
            external_url=source_url,
        ),
        scraped_at=scraped_at,
    )


def cards_to_events(
    cards: list[dict[str, Any]],
    *,
    base_url: str,
    capital_units: set[str],
    scraped_at: datetime,
) -> list[CulturalEvent]:
    """Filter cards to the capital and map them to events (pure, offline).

    A card is kept when any of its unit slugs is in ``capital_units`` and it is
    not cancelled. Extracted from :meth:`SescParser.fetch_events` so it can be
    unit-tested without touching the network.
    """
    events: list[CulturalEvent] = []
    for card in cards:
        if card.get("cancelado"):  # skip cancelled activities
            continue
        if not (set(_unit_slugs(card)) & capital_units):
            continue  # not in the capital
        event = _card_to_event(card, base_url=base_url, scraped_at=scraped_at)
        if event is not None:
            events.append(event)
    return events


class SescParser(BaseParser):
    source = "sesc"

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def can_parse(self, url: str) -> bool:
        return "sescsp.org.br" in urlparse(url).netloc

    # --- API-native collection ----------------------------------------------
    async def fetch_events(
        self,
        fetcher: Fetcher,
        *,
        scraped_at: datetime,
        max_events: int | None = None,
    ) -> list[CulturalEvent]:
        """Page through the Sesc JSON API and build capital-only events."""
        base_url = self._settings.sesc_base_url
        capital = self._settings.sesc_capital_unit_set

        events: list[CulturalEvent] = []
        seen: set[str] = set()
        page = 1
        while True:
            payload = await fetcher.fetch_json(self._page_url(base_url, page))
            cards = payload.get("atividade", []) if isinstance(payload, dict) else []
            if not cards:
                break

            for event in cards_to_events(
                cards, base_url=base_url, capital_units=capital, scraped_at=scraped_at
            ):
                if event.id in seen:
                    continue
                seen.add(event.id)
                events.append(event)
                if max_events is not None and len(events) >= max_events:
                    logger.info("sesc_collected", events=len(events), pages=page)
                    return events

            if len(cards) < _PAGE_SIZE:
                break  # last page
            page += 1

        logger.info("sesc_collected", events=len(events), pages=page)
        return events

    def _page_url(self, base_url: str, page: int) -> str:
        query = f"?ppp={_PAGE_SIZE}&page={page}"
        if self._settings.sesc_interval:
            query += f"&intervalo={self._settings.sesc_interval}"
        return urljoin(base_url, _FILTER_PATH) + query

    # --- BaseParser HTML hooks (unused: this source is API-native) -----------
    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        return []

    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        raise NotImplementedError("SescParser is API-native; use fetch_events()")
