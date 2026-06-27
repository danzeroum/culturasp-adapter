"""Unit tests for best-effort PDF OCR — no Tesseract/Poppler binaries needed.

The OCR deps (`pdf2image`, `pytesseract`) are imported lazily inside the
function, so we drive every branch by injecting fakes into ``sys.modules``.
"""

from __future__ import annotations

import sys
import types

import pytest

from culturasp.models.event import OCRStatus
from culturasp.scraper.ocr.pdf_ocr import ocr_pdf_bytes


def _install_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    pages_text: list[str],
    convert_raises: bool = False,
) -> None:
    pdf2image = types.ModuleType("pdf2image")
    pytesseract = types.ModuleType("pytesseract")

    def convert_from_bytes(data: bytes, dpi: int = 200) -> list[object]:
        if convert_raises:
            raise RuntimeError("poppler not installed")
        return [object() for _ in pages_text]

    remaining = list(pages_text)

    def image_to_string(img: object, lang: str = "por") -> str:
        return remaining.pop(0) if remaining else ""

    pdf2image.convert_from_bytes = convert_from_bytes  # type: ignore[attr-defined]
    pytesseract.image_to_string = image_to_string  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pdf2image", pdf2image)
    monkeypatch.setitem(sys.modules, "pytesseract", pytesseract)


def test_not_attempted_when_deps_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # A None entry in sys.modules makes `import pdf2image` raise ImportError,
    # deterministically exercising the "deps missing" branch.
    monkeypatch.setitem(sys.modules, "pdf2image", None)
    status, text = ocr_pdf_bytes(b"%PDF-1.4 fake")
    assert status is OCRStatus.not_attempted
    assert text is None


def test_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fakes(monkeypatch, pages_text=["Mapa de assentos", "Setor A"])
    status, text = ocr_pdf_bytes(b"%PDF-1.4 fake")
    assert status is OCRStatus.success
    assert text == "Mapa de assentos\nSetor A"


def test_failed_when_text_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fakes(monkeypatch, pages_text=[""])
    status, text = ocr_pdf_bytes(b"%PDF-1.4 fake")
    assert status is OCRStatus.failed
    assert text is None


def test_failed_on_conversion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fakes(monkeypatch, pages_text=[], convert_raises=True)
    status, text = ocr_pdf_bytes(b"%PDF-1.4 fake")
    assert status is OCRStatus.failed
    assert text is None
