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

# Accepts "20h", "20h50" and the colon form "20:00" used on the live site.
TIME_RE = re.compile(r"(\d{1,2})\s*[h:]\s*(\d{2})?")
DURATION_RE = re.compile(r"(\d+)\s*min", re.IGNORECASE)
# Live dates are prefixed with an abbreviated weekday ("seg., 20 de julho de
# 2026"). dateparser chokes on some of these abbreviations (notably "seg.")
# and returns None, so we strip the redundant weekday before parsing — the day
# number already carries the information.
_WEEKDAY_PREFIX = re.compile(r"^(?:dom|seg|ter|qua|qui|sex|s[áa]b)\.?,?\s+", re.IGNORECASE)
_YEAR_RE = re.compile(r"\b(20\d{2})\b")
# Range separators must be space-delimited so numeric dates like "10-05-2026"
# are never split on their internal hyphens.
_RANGE_SEP = re.compile(r"\s+(?:a|até|ate|to)\s+|\s+[\u2013\u2014-]\s+", re.IGNORECASE)
_ONLY_END = re.compile(r"^(?:até|ate)\s+(.*)$", re.IGNORECASE)
_ONLY_START = re.compile(r"^(?:a partir d[eo]|a partir do dia|desde)\s+(.*)$", re.IGNORECASE)
_RANGE_OPENER = re.compile(r"^(?:de|do dia)\s+", re.IGNORECASE)


def _dateparse(text: str) -> datetime | None:
    """Parse a PT-BR date, first dropping a leading weekday abbreviation."""
    return dateparser.parse(
        _WEEKDAY_PREFIX.sub("", text.strip()),
        languages=["pt"],
        settings={"DATE_ORDER": "DMY"},
    )


def _parse_ptbr_date(text: str | None) -> datetime | None:
    if not text or not text.strip():
        return None
    return _dateparse(text)


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
        base = _dateparse(date_text)
        if base and time_text:
            tm = TIME_RE.search(time_text)
            if tm:
                hour = int(tm.group(1))
                minute = int(tm.group(2) or 0)
                base = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        start = base

    end = start + timedelta(minutes=duration) if (start and duration) else None
    return start, end, duration


def parse_ptbr_date_range(text: str | None) -> tuple[datetime | None, datetime | None]:
    """Parse a PT-BR date period into ``(start, end)``.

    Handles ranges ("De 10 de maio a 20 de agosto de 2026", "10/05/2026 a
    20/08/2026"), one-sided phrases ("até …" → only end; "a partir de …" → only
    start) and a bare single date. The year is propagated from the end to the
    start when the start omits it. Unparseable input yields ``(None, None)``.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return None, None

    if m := _ONLY_END.match(cleaned):
        return None, _parse_ptbr_date(m.group(1))
    if m := _ONLY_START.match(cleaned):
        return _parse_ptbr_date(m.group(1)), None

    body = _RANGE_OPENER.sub("", cleaned)
    parts = _RANGE_SEP.split(body, maxsplit=1)
    if len(parts) == 2:
        start_text, end_text = parts[0].strip(), parts[1].strip()
        # Propagate the year from the end to the start when the start lacks one.
        if not _YEAR_RE.search(start_text) and (ym := _YEAR_RE.search(end_text)):
            start_text = f"{start_text} de {ym.group(1)}"
        return _parse_ptbr_date(start_text), _parse_ptbr_date(end_text)

    return _parse_ptbr_date(body), None


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
