"""Unit tests for the polite fetcher — robots enforcement and cache-first.

No network is touched: robots and cache are injected as fakes.
"""

from __future__ import annotations

import pytest

from culturasp.cache.redis_cache import Cache
from culturasp.core.config import Settings
from culturasp.core.exceptions import RobotsDisallowedError
from culturasp.scraper.fetcher import Fetcher


class FakeRobots:
    def __init__(self, allowed: bool) -> None:
        self._allowed = allowed

    def can_fetch(self, url: str) -> bool:
        return self._allowed


class FakeCache(Cache):
    def __init__(self, value: str | None) -> None:
        super().__init__(client=None, default_ttl=60)
        self._value = value
        self.set_calls: list[tuple[str, str]] = []

    def get(self, kind: str, key: str) -> str | None:
        return self._value

    def set(self, kind: str, key: str, value: str, ttl: int | None = None) -> None:
        self.set_calls.append((key, value))


async def test_fetch_blocked_by_robots() -> None:
    fetcher = Fetcher(
        settings=Settings(respect_robots=True),
        cache=FakeCache(None),
        robots=FakeRobots(allowed=False),  # type: ignore[arg-type]
    )
    with pytest.raises(RobotsDisallowedError):
        await fetcher.fetch("https://salasaopaulo.art.br/salasp/pt/concerto/1727")


async def test_fetch_returns_cached_without_network() -> None:
    cache = FakeCache("<html>cached</html>")
    fetcher = Fetcher(
        settings=Settings(respect_robots=True),
        cache=cache,
        robots=FakeRobots(allowed=True),  # type: ignore[arg-type]
    )
    # A cache hit must short-circuit before any browser/network call.
    html = await fetcher.fetch("https://salasaopaulo.art.br/salasp/pt/concerto/1727")
    assert html == "<html>cached</html>"
    assert cache.set_calls == []


def test_delay_respects_configured_minimum() -> None:
    fetcher = Fetcher(
        settings=Settings(scrape_delay=3.0, scrape_jitter=0.0),
        cache=FakeCache(None),
        robots=FakeRobots(allowed=True),  # type: ignore[arg-type]
    )
    assert fetcher._delay_seconds() >= 3.0
