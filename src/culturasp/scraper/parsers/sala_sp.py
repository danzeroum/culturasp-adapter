"""Parser for the Sala São Paulo / OSESP concert pages.

The site has no public API; data lives in rendered HTML and PDFs. Extraction is
**label-based** (we look for "Data:", "Horário:", "Programa", etc.) rather than
position-based, so it survives layout reshuffles. Every field is optional —
a missing value yields ``None`` and a warning, never a crash.
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from culturasp.core.exceptions import ParseError
from culturasp.core.logging import get_logger
from culturasp.models.event import CulturalEvent, ProgramItem, TicketPolicy
from culturasp.scraper.parsers._common import (
    accessibility_from_soup,
    clean_text,
    labeled_fields,
    parse_datetime,
)
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)

_CONCERT_PATH = re.compile(r"/concerto/\d+", re.IGNORECASE)


class SalaSPParser(BaseParser):
    source = "sala-sp"

    def can_parse(self, url: str) -> bool:
        host = urlparse(url).netloc
        return "salasaopaulo.art.br" in host

    # --- discovery -----------------------------------------------------------
    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(listing_html, "lxml")
        urls: list[str] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            if _CONCERT_PATH.search(href):
                full = urljoin(base_url, href.split("?")[0])
                if full not in seen:
                    seen.add(full)
                    urls.append(full)
        logger.info("listing_parsed", count=len(urls))
        return urls

    # --- event ---------------------------------------------------------------
    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        soup = BeautifulSoup(html, "lxml")

        title = clean_text(soup.h1.get_text()) if soup.h1 else None
        if not title:
            raise ParseError(f"No <h1> title found at {url}")

        labels = labeled_fields(soup)
        start, end, duration = parse_datetime(labels)

        event = CulturalEvent(
            id=f"{self.source}:{self._event_id(url)}",
            source=self.source,
            source_url=url,
            title=title,
            start=start,
            end=end,
            duration_minutes=duration,
            venue=clean_text(labels.get("local")) or "Sala São Paulo",
            conductor=clean_text(labels.get("regente") or labels.get("regência")),
            program=self._parse_program(soup),
            accessibility=accessibility_from_soup(soup),
            ticket=self._parse_ticket(soup, labels),
            seat_map_url=self._seat_map_url(soup, url),
            scraped_at=scraped_at,
        )
        return event

    def anchor_selectors(self) -> list[str]:
        return ["h1", "h2"]

    # --- helpers -------------------------------------------------------------
    @staticmethod
    def _event_id(url: str) -> str:
        match = re.search(r"/concerto/(\d+)", url)
        return match.group(1) if match else urlparse(url).path.strip("/").replace("/", "-")

    @staticmethod
    def _parse_program(soup: BeautifulSoup) -> list[ProgramItem]:
        heading = soup.find(["h2", "h3"], string=re.compile(r"programa", re.IGNORECASE))
        if not heading:
            return []
        items: list[ProgramItem] = []
        for sib in heading.find_all_next():
            if isinstance(sib, Tag) and sib.name in {"h2", "h3"} and sib is not heading:
                break
            if isinstance(sib, Tag) and sib.name in {"li", "p"}:
                text = clean_text(sib.get_text(" ", strip=True))
                if not text:
                    continue
                # "Composer — Work" / "Composer: Work" / "Composer, Work"
                parts = re.split(r"\s+[—\-:]\s+|,\s+", text, maxsplit=1)
                if len(parts) == 2:
                    items.append(ProgramItem(composer=parts[0], work=parts[1]))
                else:
                    items.append(ProgramItem(composer=None, work=text))
        return items

    @staticmethod
    def _parse_ticket(soup: BeautifulSoup, labels: dict[str, str]) -> TicketPolicy:
        page_text = soup.get_text(" ", strip=True).lower()
        free = "gratuito" in page_text or "gratuita" in page_text or "grátis" in page_text

        external: str | None = None
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            label = a.get_text(" ", strip=True).lower()
            if "ingresso" in label or "retirar" in label or "onebox" in href.lower():
                external = href
                break

        return TicketPolicy(
            free_of_charge=free,
            distribution_window=clean_text(labels.get("distribuição") or labels.get("retirada")),
            cancellation_window=clean_text(labels.get("cancelamento") or labels.get("devolução")),
            external_url=external,
        )

    @staticmethod
    def _seat_map_url(soup: BeautifulSoup, base_url: str) -> str | None:
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            label = a.get_text(" ", strip=True).lower()
            if href.lower().endswith(".pdf") and (
                "mapa" in label or "assento" in label or "mapa" in href.lower()
            ):
                return urljoin(base_url, href)
        return None
