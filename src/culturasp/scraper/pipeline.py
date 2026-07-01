"""Collection pipeline: fetch → (monitor) → parse → OCR → normalise → store.

Orchestrates a polite scrape of one source into the repository. Decoupled from
the API: the API only ever reads what the pipeline has already persisted.
"""

from __future__ import annotations

from datetime import datetime, timezone

from culturasp.core.exceptions import ParseError, RobotsDisallowedError
from culturasp.core.logging import get_logger
from culturasp.db.repository import EventRepository
from culturasp.models.event import CulturalEvent
from culturasp.scraper import monitoring
from culturasp.scraper.fetcher import Fetcher
from culturasp.scraper.ocr.pdf_ocr import ocr_pdf_bytes
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)


class ScrapePipeline:
    def __init__(
        self,
        parser: BaseParser,
        repository: EventRepository,
        fetcher: Fetcher | None = None,
        *,
        enable_ocr: bool = True,
    ) -> None:
        self._parser = parser
        self._repo = repository
        self._fetcher = fetcher or Fetcher()
        self._enable_ocr = enable_ocr

    async def run(self, listing_url: str, *, max_events: int | None = None) -> list[CulturalEvent]:
        """Scrape a source into the repository.

        API-native sources (``parser.fetch_events`` returns events) take a fast
        path; HTML sources fall back to the listing → discover → parse flow.
        """
        now = datetime.now(timezone.utc)

        api_events = await self._parser.fetch_events(
            self._fetcher, scraped_at=now, max_events=max_events
        )
        if api_events is not None:
            for event in api_events:
                if self._enable_ocr and event.seat_map_url:
                    event = await self._ocr_seat_map(event)
                self._repo.upsert(event)
            logger.info("scrape_complete", source=self._parser.source, events=len(api_events))
            return api_events

        listing_html = await self._fetcher.fetch(listing_url)
        urls = self._parser.list_event_urls(listing_html, listing_url)
        if max_events is not None:
            urls = urls[:max_events]

        collected: list[CulturalEvent] = []
        previous_sig = self._repo.get_layout_signature(self._parser.source)
        new_sig: str | None = None

        for url in urls:
            try:
                html = await self._fetcher.fetch(url)
            except RobotsDisallowedError:
                continue

            if new_sig is None:
                new_sig = monitoring.layout_signature(html, self._parser)
                monitoring.detect_change(html, self._parser, previous_sig)

            try:
                event = self._parser.parse_event(html, url, scraped_at=now)
            except ParseError as exc:
                logger.warning("parse_skipped", url=url, error=str(exc))
                continue

            if self._enable_ocr and event.seat_map_url:
                event = await self._ocr_seat_map(event)

            self._repo.upsert(event)
            collected.append(event)

        if new_sig is not None:
            self._repo.set_layout_signature(self._parser.source, new_sig)

        logger.info("scrape_complete", source=self._parser.source, events=len(collected))
        return collected

    async def _ocr_seat_map(self, event: CulturalEvent) -> CulturalEvent:
        try:
            data = await self._fetcher.fetch_bytes(str(event.seat_map_url))
        except Exception as exc:
            logger.warning("seat_map_download_failed", url=str(event.seat_map_url), error=str(exc))
            return event
        status, text = ocr_pdf_bytes(data)
        event.ocr_status = status
        event.seat_map_text = text
        return event
