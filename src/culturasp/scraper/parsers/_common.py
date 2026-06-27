"""Shared, source-agnostic parsing helpers.

These pure functions are reused across parsers (Sala SP, and the experimental
Pinacoteca parser) so label-based extraction logic lives in one place. They are
deliberately HTML-shape tolerant: missing data yields ``None``, never a crash.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

import dateparser
from bs4 import BeautifulSoup, Tag

from culturasp.models.accessibility import AccessibilityInfo

TIME_RE = re.compile(r"(\d{1,2})\s*h\s*(\d{2})?")
DURATION_RE = re.compile(r"(\d+)\s*min", re.IGNORECASE)


def clean_text(text: str | None) -> str | None:
    """Collapse whitespace and strip surrounding punctuation/colons."""
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip().strip(":").strip()
    return cleaned or None


def labeled_fields(soup: BeautifulSoup) -> dict[str, str]:
    """Collect "Label: value" pairs from block elements.

    Handles both ``<strong>Label:</strong> value`` and plain ``Label: value``
    within a single block element.
    """
    fields: dict[str, str] = {}
    for el in soup.find_all(["p", "li", "div", "span", "dd", "dt"]):
        text = el.get_text(" ", strip=True)
        if ":" in text and len(text) < 200:
            key, _, value = text.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key and value and key not in fields:
                fields[key] = value
    return fields


def parse_datetime(
    labels: dict[str, str],
) -> tuple[datetime | None, datetime | None, int | None]:
    """Derive (start, end, duration_minutes) from PT-BR labeled fields."""
    date_text = labels.get("data") or labels.get("dia")
    time_text = labels.get("horário") or labels.get("horario") or labels.get("hora")
    duration = None
    for value in labels.values():
        m = DURATION_RE.search(value)
        if m:
            duration = int(m.group(1))
            break

    start: datetime | None = None
    if date_text:
        base = dateparser.parse(date_text, languages=["pt"], settings={"DATE_ORDER": "DMY"})
        if base and time_text:
            tm = TIME_RE.search(time_text)
            if tm:
                hour = int(tm.group(1))
                minute = int(tm.group(2) or 0)
                base = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        start = base

    end = start + timedelta(minutes=duration) if (start and duration) else None
    return start, end, duration


def accessibility_from_soup(soup: BeautifulSoup) -> AccessibilityInfo:
    """Extract structured accessibility info from free-running prose."""
    page_text = soup.get_text(" ", strip=True)
    lower = page_text.lower()

    def count_near(keyword: str) -> int | None:
        # Bind to the nearest preceding number: [^\d] forbids skipping past
        # another count (e.g. "15 ... cadeirantes e 14 ... obesos").
        m = re.search(r"(\d+)[^\d]{0,40}?" + keyword, lower)
        return int(m.group(1)) if m else None

    info = AccessibilityInfo(
        sign_language="libras" in lower,
        audio_description="audiodescri" in lower,
        wheelchair_seats=count_near("cadeirant") or count_near("cadeira de rodas"),
        obese_seats=count_near("obeso"),
    )
    section = soup.find(["h2", "h3"], string=re.compile(r"acessibilidade", re.IGNORECASE))
    if section:
        notes_parts = []
        for sib in section.find_all_next():
            if isinstance(sib, Tag) and sib.name in {"h2", "h3"} and sib is not section:
                break
            if isinstance(sib, Tag) and sib.name in {"p", "li"}:
                notes_parts.append(sib.get_text(" ", strip=True))
        if notes_parts:
            info.notes = clean_text(" ".join(notes_parts))
    return info
