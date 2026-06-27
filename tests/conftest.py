"""Shared test fixtures. Everything runs offline — no network access."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def listing_html() -> str:
    return (FIXTURES / "sala_sp_listing.html").read_text(encoding="utf-8")


@pytest.fixture
def concert_html() -> str:
    return (FIXTURES / "sala_sp_concert.html").read_text(encoding="utf-8")
