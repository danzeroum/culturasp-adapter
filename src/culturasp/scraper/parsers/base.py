"""Parser interface — one parser per source.

Adding a new cultural source (Pinacoteca, Theatro Municipal, ...) means writing
a new subclass; the core pipeline and API never change. This is the extension
point that materialises "cada fonte = um parser separado".
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from culturasp.models.event import CulturalEvent


class BaseParser(ABC):
    #: Stable source slug, e.g. ``"sala-sp"``. Used in event ids and the registry.
    source: str = ""

    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """Return True if this parser handles the given URL."""

    @abstractmethod
    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        """Extract concert URLs from a rendered programme/listing page.

        URLs are *discovered* here — never hardcoded — per the project's
        "no invented URLs" rule.
        """

    @abstractmethod
    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        """Parse a single rendered event page into a CulturalEvent."""

    def anchor_selectors(self) -> list[str]:
        """CSS selectors whose presence defines "the layout we expect".

        The monitor hashes these to detect layout changes. Default: title.
        """
        return ["h1"]
