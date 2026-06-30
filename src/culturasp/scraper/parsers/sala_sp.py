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

# Matches both absolute ("/salasp/pt/concerto/1727") and relative ("concerto/1586")
# hrefs — the live listing uses the relative form. urljoin() resolves them.
_CONCERT_PATH = re.compile(r"(?:^|/)concerto/\d+", re.IGNORECASE)

# On the live site the programme is a single run-on line where each composer's
# name is printed in UPPERCASE (2-4 consecutive all-caps words); the work runs
# until the next such name. Descriptive paragraphs use ordinary title case, so
# they contain no match and are skipped. Char classes intentionally include the
# curly apostrophe found in some names.
_NAME_UPPER = r"[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ'’\-]+"  # noqa: RUF001
_NAME_TITLE = r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’.\-]+"  # noqa: RUF001
_COMPOSER_RE = re.compile(rf"(?:{_NAME_UPPER}\s+){{1,3}}{_NAME_UPPER}")
# Best-effort conductor: only the explicit "regência de <Name>" phrasing, so a
# missing one stays None rather than guessing.
_CONDUCTOR_RE = re.compile(rf"[Rr]eg[êe]ncia\s+d[eo]\s+({_NAME_TITLE}(?:\s+{_NAME_TITLE}){{1,3}})")


def _split_caps_program(text: str) -> list[ProgramItem]:
    """Split a run-on programme line into items by its UPPERCASE composer names."""
    matches = list(_COMPOSER_RE.finditer(text))
    items: list[ProgramItem] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        work = text[m.end() : end].strip(" ,;:–—-")  # noqa: RUF001
        items.append(ProgramItem(composer=m.group().strip().title(), work=work or None))
    return items


def _split_dash_item(text: str) -> ProgramItem:
    """Split a single ``Composer - Work`` list entry."""
    parts = re.split(r"\s+[—\-:]\s+|,\s+", text, maxsplit=1)
    if len(parts) == 2:
        return ProgramItem(composer=parts[0], work=parts[1])
    return ProgramItem(composer=None, work=text)


def _find_conductor(soup: BeautifulSoup) -> str | None:
    m = _CONDUCTOR_RE.search(soup.get_text(" ", strip=True))
    return m.group(1) if m else None


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

        # Concert pages render two <h1>s — an empty one (logo/skip target) and
        # the real title — so take the first non-empty heading, not just soup.h1.
        title = next(
            (t for h1 in soup.find_all("h1") if (t := clean_text(h1.get_text()))),
            None,
        )
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
            conductor=clean_text(labels.get("regente") or labels.get("regência"))
            or _find_conductor(soup),
            program=self._parse_program(soup),
            accessibility=accessibility_from_soup(soup),
            ticket=self._parse_ticket(soup, labels, url),
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
            if not (isinstance(sib, Tag) and sib.name in {"li", "p"}):
                continue
            text = clean_text(sib.get_text(" ", strip=True))
            if not text:
                continue
            caps = _split_caps_program(text)
            if caps:
                items.extend(caps)  # run-on line with UPPERCASE composers
            elif sib.name == "li":
                items.append(_split_dash_item(text))  # explicit list entry
            # a <p> with neither is descriptive prose — skip it
        return items

    @staticmethod
    def _parse_ticket(soup: BeautifulSoup, labels: dict[str, str], base_url: str) -> TicketPolicy:
        page_text = soup.get_text(" ", strip=True).lower()
        free = "gratuito" in page_text or "gratuita" in page_text or "grátis" in page_text

        external: str | None = None
        for a in soup.find_all("a", href=True):
            href = str(a["href"])
            label = a.get_text(" ", strip=True).lower()
            if "ingresso" in label or "retirar" in label or "onebox" in href.lower():
                # Ticket hrefs are often relative ("/osesp/pt/..."); external_url
                # requires an absolute URL, so resolve against the page URL.
                external = urljoin(base_url, href)
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
