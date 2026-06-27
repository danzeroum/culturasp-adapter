"""Layout-change detection.

We hash the set of "anchor" selectors a parser declares as defining the layout
it expects. If, on a later run, those anchors no longer all resolve, the page
structure likely changed and downstream extraction can silently degrade — so we
emit an alert. The previous hash is persisted (Postgres) per source.
"""

from __future__ import annotations

import hashlib

import httpx
from bs4 import BeautifulSoup

from culturasp.core.config import get_settings
from culturasp.core.logging import get_logger
from culturasp.scraper.parsers.base import BaseParser

logger = get_logger(__name__)


def layout_signature(html: str, parser: BaseParser) -> str:
    """Compute a stable signature of the layout's anchor selectors.

    The signature encodes, for each anchor selector, whether it matches and how
    many times. A structural change flips the count and thus the hash.
    """
    soup = BeautifulSoup(html, "lxml")
    parts = []
    for selector in parser.anchor_selectors():
        count = len(soup.select(selector))
        parts.append(f"{selector}={count}")
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return digest


def detect_change(html: str, parser: BaseParser, previous_signature: str | None) -> bool:
    """Return True if the layout changed vs the previous signature."""
    current = layout_signature(html, parser)
    if previous_signature is None:
        return False
    changed = current != previous_signature
    if changed:
        logger.warning(
            "layout_changed", source=parser.source, previous=previous_signature, current=current
        )
        _alert(parser.source, previous_signature, current)
    return changed


def _alert(source: str, previous: str, current: str) -> None:
    """Send an optional webhook alert; always at least logs."""
    settings = get_settings()
    if not settings.alert_webhook_url:
        return
    try:
        httpx.post(
            settings.alert_webhook_url,
            json={
                "type": "layout_changed",
                "source": source,
                "previous_signature": previous,
                "current_signature": current,
            },
            timeout=10,
        )
    except httpx.HTTPError as exc:  # pragma: no cover - network path
        logger.warning("alert_webhook_failed", error=str(exc))
