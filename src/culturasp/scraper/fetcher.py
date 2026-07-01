"""Polite, cache-first page fetcher.

Responsibilities (the "ethical" core of the scraper):
  * respect robots.txt before every URL,
  * serve from the Redis cache when fresh (avoids repeated requests),
  * enforce a configurable delay + jitter between live requests,
  * render via Playwright with an identifiable User-Agent.

The fetcher is the only component allowed to touch the network.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import httpx

from culturasp.cache import Cache, get_cache
from culturasp.core.config import Settings, get_settings
from culturasp.core.exceptions import RobotsDisallowedError
from culturasp.core.logging import get_logger
from culturasp.scraper.browser import browser_context, render_html

logger = get_logger(__name__)


class RobotsChecker:
    """Caches one parsed robots.txt per host."""

    def __init__(self, user_agent: str) -> None:
        self._user_agent = user_agent
        self._parsers: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _parser_for(self, url: str) -> urllib.robotparser.RobotFileParser:
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        if host not in self._parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = urljoin(host, "/robots.txt")
            try:
                # Fetch via httpx, which transparently decompresses gzip/deflate.
                # urllib's own reader does NOT decompress, so a gzip-encoded
                # robots.txt raises a decode error and leaves the parser "unread"
                # — and an unread RobotFileParser makes can_fetch() deny *every*
                # URL, silently blocking all scraping. A 4xx (no robots.txt) or a
                # transport/parse failure must fail open, not closed.
                resp = httpx.get(
                    robots_url,
                    headers={"User-Agent": self._user_agent},
                    timeout=10,
                    follow_redirects=True,
                )
                rp.parse(resp.text.splitlines() if resp.status_code < 400 else [])
            except Exception as exc:
                logger.warning("robots_read_failed", host=host, error=str(exc))
                rp.parse([])  # permissive on technical failure
            self._parsers[host] = rp
        return self._parsers[host]

    def can_fetch(self, url: str) -> bool:
        return self._parser_for(url).can_fetch(self._user_agent, url)


class Fetcher:
    """Fetches rendered HTML, cache-first and politely."""

    def __init__(
        self,
        settings: Settings | None = None,
        cache: Cache | None = None,
        robots: RobotsChecker | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._cache = cache or get_cache()
        self._robots = robots or RobotsChecker(self._settings.user_agent)

    def _delay_seconds(self) -> float:
        # secrets is used purely for jitter; Date/random restrictions don't apply here.
        jitter = self._settings.scrape_jitter * (secrets.randbelow(1000) / 1000)
        return self._settings.scrape_delay + jitter

    async def fetch(
        self, url: str, *, wait_selector: str | None = None, use_cache: bool = True
    ) -> str:
        """Return rendered HTML for ``url``.

        Raises :class:`RobotsDisallowedError` if robots.txt forbids the URL.
        """
        if self._settings.respect_robots and not self._robots.can_fetch(url):
            logger.warning("robots_disallowed", url=url)
            raise RobotsDisallowedError(url)

        if use_cache:
            cached = self._cache.get("page", url)
            if cached is not None:
                logger.info("cache_hit", url=url)
                return cached

        logger.info("fetch_live", url=url, delay=round(self._delay_seconds(), 2))
        async with browser_context() as ctx:
            await asyncio.sleep(self._delay_seconds())
            html = await render_html(ctx, url, wait_selector=wait_selector)

        self._cache.set("page", url, html)
        return html

    async def fetch_json(self, url: str, *, use_cache: bool = True) -> object:
        """Fetch and decode a JSON endpoint politely.

        Used by API-native sources (e.g. Sesc's WordPress JSON API). Unlike
        :meth:`fetch`, this goes straight through httpx — the payload is JSON, so
        there is nothing for a headless browser to render. Honours robots.txt,
        the inter-request delay and the cache (keyed under ``"json"``).
        """
        if self._settings.respect_robots and not self._robots.can_fetch(url):
            logger.warning("robots_disallowed", url=url)
            raise RobotsDisallowedError(url)

        if use_cache:
            cached = self._cache.get("json", url)
            if cached is not None:
                logger.info("cache_hit", url=url)
                return json.loads(cached)

        logger.info("fetch_json_live", url=url)
        await asyncio.sleep(self._delay_seconds())
        async with httpx.AsyncClient(
            headers={"User-Agent": self._settings.user_agent}, timeout=30, follow_redirects=True
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            self._cache.set("json", url, resp.text)
            return resp.json()

    async def fetch_bytes(self, url: str) -> bytes:
        """Download a binary asset (e.g. a seat-map PDF) politely.

        Honours robots.txt and the inter-request delay, with the same UA.
        """
        if self._settings.respect_robots and not self._robots.can_fetch(url):
            logger.warning("robots_disallowed", url=url)
            raise RobotsDisallowedError(url)
        await asyncio.sleep(self._delay_seconds())
        async with httpx.AsyncClient(
            headers={"User-Agent": self._settings.user_agent}, timeout=30, follow_redirects=True
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
