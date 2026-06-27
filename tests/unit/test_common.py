"""Unit tests for shared parser helpers (parsers/_common.py)."""

from __future__ import annotations

import pytest

from culturasp.scraper.parsers._common import parse_ptbr_date_range


def _ymd(dt) -> tuple[int, int, int] | None:
    return (dt.year, dt.month, dt.day) if dt else None


def test_range_full_words_with_year_propagation() -> None:
    start, end = parse_ptbr_date_range("De 10 de maio a 20 de agosto de 2026")
    assert _ymd(start) == (2026, 5, 10)  # year propagated from the end
    assert _ymd(end) == (2026, 8, 20)


def test_range_numeric() -> None:
    start, end = parse_ptbr_date_range("10/05/2026 a 20/08/2026")
    assert _ymd(start) == (2026, 5, 10)
    assert _ymd(end) == (2026, 8, 20)


def test_range_with_dash() -> None:
    start, end = parse_ptbr_date_range("10 de maio \u2013 20 de agosto de 2026")
    assert _ymd(start) == (2026, 5, 10)
    assert _ymd(end) == (2026, 8, 20)


def test_only_end() -> None:
    start, end = parse_ptbr_date_range("até 20 de agosto de 2026")
    assert start is None
    assert _ymd(end) == (2026, 8, 20)


def test_only_start() -> None:
    start, end = parse_ptbr_date_range("a partir de 10 de maio de 2026")
    assert _ymd(start) == (2026, 5, 10)
    assert end is None


def test_numeric_date_not_split_on_internal_hyphen() -> None:
    # A single numeric date must not be torn apart on its own hyphens.
    start, end = parse_ptbr_date_range("10-05-2026")
    assert _ymd(start) == (2026, 5, 10)
    assert end is None


@pytest.mark.parametrize("text", ["", None, "   ", "sem informação"])
def test_unparseable_yields_none(text: str | None) -> None:
    assert parse_ptbr_date_range(text) == (None, None)
