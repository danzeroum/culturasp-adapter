"""EXPERIMENTAL candidate parser for the Pinacoteca de São Paulo.

⚠️  NOT VERIFIED against real pages and NOT registered in the live ``PARSERS``
    registry — it is exposed only via ``EXPERIMENTAL_PARSERS``/``ALL_PARSERS`` so
    it can be validated. The selectors below are BEST-GUESS placeholders marked
    "A CONFIRMAR"; confirm/adjust them against a real snapshot:

        python scripts/capture_fixture.py --source pinacoteca \\
            --listing-url "<URL real da programação/exposições>"

Remaining caveat before promoting this to a live source (adding it to ``PARSERS``):

- **Date ranges.** Exhibitions run over a period ("de … a …"); the shared
  ``parse_datetime`` extracts a single start, so the end/period handling will
  need refinement.

The schema.org type is already handled: this parser sets
``schema_type=ExhibitionEvent``, and ``models/jsonld.event_to_jsonld`` maps it to
``schema.org/ExhibitionEvent`` (omitting music-only properties).

The host (``pinacoteca.org.br``) is the real, well-known domain; no event paths
are hardcoded — they are discovered at runtime from the listing page.
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
    parse_datetime,
)
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)

# A CONFIRMAR: padrão de path das páginas de exposição/evento. Ajuste contra um
# snapshot real (ex.: "/exposicao/<slug>" ou "/programacao/<id>").
_EVENT_PATH = re.compile(r"/(exposicao|exposicoes|programacao|evento)s?/[\w-]+", re.IGNORECASE)


class PinacotecaParser(BaseParser):
    """Experimental — confirm every selector against a real fixture."""

    source = "pinacoteca"
    _host = "pinacoteca.org.br"

    def can_parse(self, url: str) -> bool:
        return self._host in urlparse(url).netloc

    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        # A CONFIRMAR: descobre os links de exposição/evento na listagem renderizada.
        soup = BeautifulSoup(listing_html, "lxml")
        urls: list[str] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            if _EVENT_PATH.search(href):
                full = urljoin(base_url, href.split("?")[0])
                if full not in seen:
                    seen.add(full)
                    urls.append(full)
        logger.info("listing_parsed", source=self.source, count=len(urls))
        return urls

    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        soup = BeautifulSoup(html, "lxml")

        # A CONFIRMAR: o título costuma estar no <h1>.
        title = clean_text(soup.h1.get_text()) if soup.h1 else None
        if not title:
            raise ParseError(f"No <h1> title found at {url}")

        labels = labeled_fields(soup)
        start, end, _duration = parse_datetime(labels)

        return CulturalEvent(
            id=f"{self.source}:{self._event_id(url)}",
            source=self.source,
            source_url=url,
            title=title,
            schema_type=SchemaType.exhibition_event,  # museu → exposição
            start=start,
            end=end,
            # A CONFIRMAR: rótulo do local; default para a instituição.
            venue=clean_text(labels.get("local") or labels.get("endereço"))
            or "Pinacoteca de São Paulo",
            program=[],  # museu: sem "programa" de obras como num concerto
            conductor=None,
            accessibility=accessibility_from_soup(soup),
            ticket=self._parse_ticket(soup, labels),
            scraped_at=scraped_at,
        )

    def anchor_selectors(self) -> list[str]:
        # A CONFIRMAR: âncoras que definem o layout esperado (para o monitor).
        return ["h1"]

    @staticmethod
    def _event_id(url: str) -> str:
        path = urlparse(url).path.strip("/")
        return path.rsplit("/", 1)[-1] if path else url

    @staticmethod
    def _parse_ticket(soup: BeautifulSoup, labels: dict[str, str]) -> TicketPolicy:
        # A CONFIRMAR: a Pinacoteca tem entrada paga/gratuita conforme o dia;
        # aqui apenas detectamos gratuidade pelo texto e o link oficial.
        page_text = soup.get_text(" ", strip=True).lower()
        free = "gratuito" in page_text or "gratuita" in page_text or "grátis" in page_text

        external: str | None = None
        for a in soup.find_all("a", href=True):
            label = a.get_text(" ", strip=True).lower()
            if "ingresso" in label or "agende" in label or "visita" in label:
                external = str(a["href"])
                break

        return TicketPolicy(free_of_charge=free, external_url=external)
