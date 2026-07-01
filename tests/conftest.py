"""Shared test fixtures. Everything runs offline — no network access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def listing_html() -> str:
    return (FIXTURES / "sala_sp_listing.html").read_text(encoding="utf-8")


@pytest.fixture
def concert_html() -> str:
    return (FIXTURES / "sala_sp_concert.html").read_text(encoding="utf-8")


@pytest.fixture
def sesc_filter_payload() -> dict[str, Any]:
    return json.loads((FIXTURES / "sesc_filter.json").read_text(encoding="utf-8"))
