"""Capture real source snapshots for use as offline test fixtures.

Run this **locally** (where you have network access) to politely snapshot a
source's listing + a few event pages into ``tests/fixtures/real/``, then commit
the snapshots so the parser can be validated/regression-tested offline.

It reuses the project's ethical :class:`Fetcher` (robots.txt + delay + cache),
so capturing respects the same politeness rules as the scraper. It also prints a
parse-health report so you can immediately see whether the selectors still work.

Usage:
    pip install -e ".[dev]"
    playwright install chromium
    python scripts/capture_fixture.py --source sala-sp --max 2

Note: this script touches the network on purpose; it is never run in CI.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path

from culturasp.core.config import get_settings
from culturasp.scraper.cli import LISTING_PATHS
from culturasp.scraper.fetcher import Fetcher
from culturasp.scraper.parsers import PARSERS

OUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "real"


def _slug(url: str) -> str:
    m = re.search(r"/(\d+)(?:[/?#]|$)", url)
    return m.group(1) if m else re.sub(r"\W+", "-", url)[-40:].strip("-")


async def _capture(source: str, max_events: int) -> None:
    settings = get_settings()
    parser = PARSERS[source]
    fetcher = Fetcher()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    listing_url = settings.sala_sp_base_url + LISTING_PATHS[source]
    print(f"→ fetching listing: {listing_url}")
    listing_html = await fetcher.fetch(listing_url, use_cache=False)
    (OUT_DIR / f"{source}_listing.html").write_text(listing_html, encoding="utf-8")

    urls = parser.list_event_urls(listing_html, listing_url)
    print(f"  discovered {len(urls)} event URLs; capturing up to {max_events}")
    if not urls:
        print("  ⚠ no event URLs found — the listing selectors may have changed.")
        return

    now = datetime.now(timezone.utc)
    for url in urls[:max_events]:
        print(f"→ fetching event: {url}")
        html = await fetcher.fetch(url, use_cache=False)
        (OUT_DIR / f"{source}_concert_{_slug(url)}.html").write_text(html, encoding="utf-8")
        try:
            event = parser.parse_event(html, url, scraped_at=now)
        except Exception as exc:  # diagnostic report — any parse failure is shown
            print(f"  ✗ parse FAILED: {exc!r}")
            continue
        print(
            "  ✓ parsed: "
            f"title={event.title!r} start={event.start} "
            f"program={len(event.program)} items "
            f"accessibility(any={event.accessibility.has_any}) "
            f"seat_map={'yes' if event.seat_map_url else 'no'}"
        )

    print(f"\nSaved snapshots to {OUT_DIR}. Review, trim if large, and commit them.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Capture real source snapshots (run locally).")
    ap.add_argument("--source", default="sala-sp", choices=sorted(PARSERS))
    ap.add_argument("--max", type=int, default=2, help="Max event pages to capture")
    args = ap.parse_args()
    asyncio.run(_capture(args.source, args.max))


if __name__ == "__main__":
    main()
