"""End-to-end pipeline test: listing → fetch → parse → store → serve.

The network layer (Fetcher) is replaced with a fake that serves saved fixtures,
so the full pipeline runs offline and deterministically.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from culturasp.api.deps import get_event_repository
from culturasp.api.main import app
from culturasp.db.repository import InMemoryEventRepository
from culturasp.scraper.parsers.sala_sp import SalaSPParser
from culturasp.scraper.pipeline import ScrapePipeline


class FakeFetcher:
    """Serves fixtures instead of hitting the network."""

    def __init__(self, listing: str, concert: str) -> None:
        self._listing = listing
        self._concert = concert

    async def fetch(self, url: str, **_: object) -> str:
        return self._concert if "concerto" in url else self._listing

    async def fetch_bytes(self, url: str) -> bytes:  # pragma: no cover - OCR disabled here
        raise AssertionError("network should not be touched in e2e test")


@pytest.mark.e2e
async def test_full_pipeline_to_api(listing_html: str, concert_html: str) -> None:
    repo = InMemoryEventRepository()
    pipeline = ScrapePipeline(
        SalaSPParser(),
        repo,
        fetcher=FakeFetcher(listing_html, concert_html),  # type: ignore[arg-type]
        enable_ocr=False,
    )

    events = await pipeline.run("https://salasaopaulo.art.br/salasp/pt/programacao")

    # Two concert links were discovered in the listing fixture.
    assert len(events) == 2
    assert repo.count() == 2
    assert {e.id for e in events} == {"sala-sp:1727", "sala-sp:1801"}
    # Layout signature persisted for monitoring.
    assert repo.get_layout_signature("sala-sp") is not None

    # The stored data is now served by the API.
    app.dependency_overrides[get_event_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            listed = client.get("/v1/events").json()
            assert len(listed) == 2
            doc = client.get("/v1/events/sala-sp:1727/jsonld").json()
            assert doc["@type"] == "MusicEvent"
    finally:
        app.dependency_overrides.clear()
