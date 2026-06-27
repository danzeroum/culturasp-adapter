"""Golden regression tests against real captured snapshots.

These run automatically over any ``tests/fixtures/real/*_concert_*.html`` that a
contributor has captured with ``scripts/capture_fixture.py``. They are SKIPPED
while no real fixtures exist, so CI stays green out of the box but gains real
coverage the moment a snapshot is committed.

The snapshot filename encodes the source slug as its prefix:
``<source>_concert_<id>.html`` → parser looked up from ``PARSERS``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from culturasp.models.event import CulturalEvent
from culturasp.scraper.parsers import PARSERS

REAL_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "real"
CONCERTS = sorted(REAL_DIR.glob("*_concert_*.html"))


@pytest.mark.skipif(
    not CONCERTS,
    reason="no real fixtures captured yet — run scripts/capture_fixture.py locally",
)
@pytest.mark.parametrize("path", CONCERTS or [None], ids=lambda p: p.name if p else "none")
def test_real_concert_parses(path: Path) -> None:
    source = path.name.split("_concert_")[0]
    parser = PARSERS.get(source)
    assert parser is not None, f"no parser registered for source {source!r}"

    html = path.read_text(encoding="utf-8")
    url = f"https://{parser.source}.example/concerto/{path.stem}"
    event = parser.parse_event(html, url, scraped_at=datetime.now(timezone.utc))

    # Invariants that must hold for any real, parseable event page.
    assert isinstance(event, CulturalEvent)
    assert event.title and event.title.strip()
    assert event.id.startswith(f"{parser.source}:")
    assert str(event.source_url)
