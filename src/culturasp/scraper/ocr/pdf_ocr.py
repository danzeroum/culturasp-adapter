"""Best-effort OCR for attached PDFs (seat maps / printed programmes).

OCR is optional (extras ``[ocr]``) and never fatal: any failure returns
``(OCRStatus.failed, None)`` so the event is still served without the map.
"""

from __future__ import annotations

from culturasp.core.logging import get_logger
from culturasp.models.event import OCRStatus

logger = get_logger(__name__)


def ocr_pdf_bytes(
    data: bytes, *, lang: str = "por", dpi: int = 200
) -> tuple[OCRStatus, str | None]:
    """Run OCR over PDF bytes. Returns (status, extracted_text)."""
    try:
        import pdf2image
        import pytesseract
    except ImportError:
        logger.warning("ocr_deps_missing", hint="install extras: pip install '.[ocr]'")
        return OCRStatus.not_attempted, None

    try:
        images = pdf2image.convert_from_bytes(data, dpi=dpi)
        text = "\n".join(pytesseract.image_to_string(img, lang=lang) for img in images)
        text = text.strip()
        if not text:
            return OCRStatus.failed, None
        return OCRStatus.success, text
    except Exception as exc:
        logger.warning("ocr_failed", error=str(exc))
        return OCRStatus.failed, None
