"""Unit test for the scheduler's collect_all resilience.

A failure collecting one source must be logged and must NOT abort the loop —
the remaining sources still run.
"""

from __future__ import annotations

from typing import ClassVar

import pytest

from culturasp.scraper import scheduler as sched


class _FakeParser:
    def __init__(self, source: str) -> None:
        self.source = source


class _FakePipeline:
    #: records the sources whose run() was attempted
    attempted: ClassVar[list[str]] = []

    def __init__(self, parser: _FakeParser, repo: object) -> None:
        self._parser = parser

    async def run(self, listing_url: str) -> list:
        _FakePipeline.attempted.append(self._parser.source)
        if self._parser.source == "broken":
            raise RuntimeError("source down")
        return []


async def test_collect_all_continues_after_one_source_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _FakePipeline.attempted = []
    monkeypatch.setattr(sched, "get_repository", lambda: object())
    monkeypatch.setattr(sched, "ScrapePipeline", _FakePipeline)
    monkeypatch.setattr(
        sched, "PARSERS", {"broken": _FakeParser("broken"), "ok": _FakeParser("ok")}
    )
    # collect_all resolves each source's listing URL via listing_url_for(source, settings);
    # stub it so the test doesn't depend on any real source's configured path.
    monkeypatch.setattr(sched, "listing_url_for", lambda source, settings: f"/{source}")

    await sched.collect_all()

    # Both sources were attempted despite the first one raising.
    assert _FakePipeline.attempted == ["broken", "ok"]
