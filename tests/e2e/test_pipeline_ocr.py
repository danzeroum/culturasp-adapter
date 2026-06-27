"""E2E: pipeline with OCR enabled — seat-map PDF is downloaded and OCR'd.

Network (Fetcher) and OCR are both faked, so the full
fetch→parse→ocr→store path runs offline.
"""

from __future__ import annotations

import pytest

from culturasp.db.repository import InMemoryEventRepository
from culturasp.models.event import OCRStatus
from culturasp.scraper import pipeline as pipeline_mod
from culturasp.scraper.parsers.sala_sp import SalaSPParser
from culturasp.scraper.pipeline import ScrapePipeline


class FakeFetcher:
    def __init__(self, listing: str, concert: str) -> None:
        self._listing = listing
        self._concert = concert
        self.bytes_calls: list[str] = []

    async def fetch(self, url: str, **_: object) -> str:
        return self._concert if "concerto" in url else self._listing

    async def fetch_bytes(self, url: str) -> bytes:
        self.bytes_calls.append(url)
        return b"%PDF-1.4 fake seat map"


@pytest.mark.e2e
async def test_pipeline_runs_ocr_on_seat_map(
    monkeypatch: pytest.MonkeyPatch, listing_html: str, concert_html: str
) -> None:
    # Force a deterministic OCR result without Tesseract/Poppler.
    monkeypatch.setattr(
        pipeline_mod,
        "ocr_pdf_bytes",
        lambda data: (OCRStatus.success, "Mapa de assentos — Setor A"),
    )

    repo = InMemoryEventRepository()
    fetcher = FakeFetcher(listing_html, concert_html)
    pipeline = ScrapePipeline(
        SalaSPParser(),
        repo,
        fetcher=fetcher,  # type: ignore[arg-type]
        enable_ocr=True,
    )

    events = await pipeline.run("https://salasaopaulo.art.br/salasp/pt/programacao")

    assert len(events) == 2
    # Both concert fixtures expose a seat-map PDF → both were downloaded + OCR'd.
    assert len(fetcher.bytes_calls) == 2
    for event in events:
        assert event.ocr_status is OCRStatus.success
        assert event.seat_map_text == "Mapa de assentos — Setor A"
