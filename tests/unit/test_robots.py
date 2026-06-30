"""Unit tests for robots.txt handling — fail-open on technical failure."""

from __future__ import annotations

import httpx
import pytest

from culturasp.scraper.fetcher import RobotsChecker


def _patch_get(monkeypatch: pytest.MonkeyPatch, fn) -> None:
    monkeypatch.setattr(httpx, "get", fn)


def test_allows_when_robots_unreadable(monkeypatch: pytest.MonkeyPatch) -> None:
    # A gzip-encoded body or transport error must not block every URL.
    def boom(*_a: object, **_k: object) -> httpx.Response:
        raise httpx.ConnectError("boom")

    _patch_get(monkeypatch, boom)
    assert RobotsChecker("UA").can_fetch("https://x/y") is True


def test_allows_when_robots_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_get(monkeypatch, lambda *_a, **_k: httpx.Response(404, text="nope"))
    assert RobotsChecker("UA").can_fetch("https://x/y") is True


def test_respects_disallow_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    body = "User-agent: *\nDisallow: /private\n"
    _patch_get(monkeypatch, lambda *_a, **_k: httpx.Response(200, text=body))
    rc = RobotsChecker("UA")
    assert rc.can_fetch("https://x/private/p") is False
    assert rc.can_fetch("https://x/public") is True
