"""EXPERIMENTAL candidate parser for SESC São Paulo — children's programming.

⚠️  NOT VERIFIED against real pages and NOT registered in the live ``PARSERS``
    registry — it is exposed only via ``EXPERIMENTAL_PARSERS``/``ALL_PARSERS`` so
    it can be validated. Several selectors below are BEST-GUESS placeholders
    marked "A CONFIRMAR"; confirm/adjust them against a real snapshot:

        python scripts/capture_fixture.py --source sesc-sp \\
            --listing-url "https://www.sescsp.org.br/programacao/infantil/"

What is CONFIRMED about the source (checked live):
- ``www.sescsp.org.br`` is a WordPress site; ``robots.txt`` allows crawling
  (``Disallow:`` empty).
- The programme listing is rendered client-side by a React plugin
  ("sesc-eventos"), so the listing MUST be fetched with the project's Playwright
  fetcher — a plain GET returns an empty shell with no event links.
- Event detail pages live under ``/programacao/<slug>`` (WordPress single-post
  permalinks); ``/programacao`` and ``/programacao/feed`` are not events.

What is still "A CONFIRMAR" (needs a real fixture):
- The exact label wording on the event page (date/time/unit/age-rating labels).
- The age-rating label ("Classificação etária", "Recomendação", "Faixa etária").

This parser targets SESC's **children's** programme, so it sets
``schema_type=ChildrensEvent`` and ``audience="infantil"`` by default, refining
the age band from the page's age-rating text via ``parse_age_range`` when found.
No event paths are hardcoded — they are discovered from the listing at runtime.
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from culturasp.core.exceptions import ParseError
from culturasp.core.logging import get_logger
from culturasp.models.event import CulturalEvent, SchemaType, TicketPolicy
from culturasp.scraper.parsers._common import (
    accessibility_from_soup,
    clean_text,
    labeled_fields,
    parse_age_range,
    parse_datetime,
    parse_ptbr_date_range,
)
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)

# Event detail permalinks: "/programacao/<slug>". Excludes the listing root and
# its feed. A CONFIRMAR: confirm no other non-event children live under this path.
_EVENT_PATH = re.compile(r"^/programacao/(?!feed(?:/|$))[\w-]+/?$", re.IGNORECASE)
_NON_EVENT_SLUGS = {"", "feed", "infantil", "categoria", "tag", "unidade"}


class SescSPParser(BaseParser):
    """Experimental — confirm every "A CONFIRMAR" selector against a real fixture."""

    source = "sesc-sp"
    _host = "sescsp.org.br"

    def can_parse(self, url: str) -> bool:
        return self._host in urlparse(url).netloc

    # --- discovery -----------------------------------------------------------
    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(listing_html, "lxml")
        urls: list[str] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            path = urlparse(urljoin(base_url, href)).path
            if not _EVENT_PATH.match(path):
                continue
            slug = path.strip("/").split("/")[-1].lower()
            if slug in _NON_EVENT_SLUGS:
                continue
            full = urljoin(base_url, href.split("?")[0])
            if full not in seen:
                seen.add(full)
                urls.append(full)
        logger.info("listing_parsed", source=self.source, count=len(urls))
        return urls

    # --- event ---------------------------------------------------------------
    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        soup = BeautifulSoup(html, "lxml")

        title = next(
            (t for h1 in soup.find_all("h1") if (t := clean_text(h1.get_text()))),
            None,
        )
        if not title:
            raise ParseError(f"No <h1> title found at {url}")

        labels = labeled_fields(soup)
        start, end, duration = parse_datetime(labels)
        if start is None:
            # Some SESC pages publish a season/period rather than a single date.
            period = (
                labels.get("período")
                or labels.get("periodo")
                or labels.get("temporada")
                or labels.get("quando")
            )
            start, end = parse_ptbr_date_range(period)

        min_age, max_age, audience = self._parse_age(soup, labels)

        return CulturalEvent(
            id=f"{self.source}:{self._event_id(url)}",
            source=self.source,
            source_url=url,
            title=title,
            schema_type=SchemaType.childrens_event,
            start=start,
            end=end,
            duration_minutes=duration,
            # A CONFIRMAR: rótulo da unidade (Pompeia/Belenzinho/...). SESC is a
            # network of units, so the venue is the specific unit when published.
            venue=clean_text(labels.get("unidade") or labels.get("local") or labels.get("onde"))
            or "SESC São Paulo",
            min_age=min_age,
            max_age=max_age,
            audience=audience,
            category=self._parse_category(labels),
            accessibility=accessibility_from_soup(soup),
            ticket=self._parse_ticket(soup, labels, url),
            scraped_at=scraped_at,
        )

    def anchor_selectors(self) -> list[str]:
        return ["h1"]

    # --- helpers -------------------------------------------------------------
    @staticmethod
    def _event_id(url: str) -> str:
        path = urlparse(url).path.strip("/")
        return path.rsplit("/", 1)[-1] if path else url

    @staticmethod
    def _parse_age(
        soup: BeautifulSoup, labels: dict[str, str]
    ) -> tuple[int | None, int | None, str]:
        """Resolve the recommended age band, defaulting to the 'infantil' audience.

        A CONFIRMAR: the age-rating label wording. We try the common phrasings and
        fall back to scanning the page prose for an age expression.
        """
        rating = (
            labels.get("classificação")
            or labels.get("classificacao")
            or labels.get("classificação etária")
            or labels.get("classificacao etaria")
            or labels.get("faixa etária")
            or labels.get("faixa etaria")
            or labels.get("recomendação")
            or labels.get("recomendacao")
            or labels.get("indicação")
            or labels.get("indicacao")
        )
        min_age, max_age, label = parse_age_range(rating)
        if min_age is None and max_age is None and label is None:
            # Fall back to the page text (e.g. "recomendado para crianças a partir
            # de 4 anos") without over-matching unrelated numbers.
            m = re.search(r"[^.]*\b\d{1,2}\s*anos[^.]*", soup.get_text(" ", strip=True))
            if m:
                min_age, max_age, label = parse_age_range(m.group(0))
        # This is the children's programme; keep 'infantil' as the audience unless
        # the rating explicitly says "livre".
        return min_age, max_age, label or "infantil"

    @staticmethod
    def _parse_category(labels: dict[str, str]) -> str | None:
        # A CONFIRMAR: SESC tags events by "Linguagem"/"Tipo" (Teatro, Música,
        # Literatura, Cursos...). Use it as the activity category when present.
        return clean_text(
            labels.get("linguagem")
            or labels.get("tipo")
            or labels.get("categoria")
            or labels.get("atividade")
        )

    @staticmethod
    def _parse_ticket(soup: BeautifulSoup, labels: dict[str, str], base_url: str) -> TicketPolicy:
        page_text = soup.get_text(" ", strip=True).lower()
        free = "gratuito" in page_text or "gratuita" in page_text or "grátis" in page_text

        external: str | None = None
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            label = a.get_text(" ", strip=True).lower()
            if "ingresso" in label or "credencial" in label or "bilheteria" in href.lower():
                external = urljoin(base_url, href)
                break

        return TicketPolicy(free_of_charge=free, external_url=external)
