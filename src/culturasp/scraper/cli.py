"""One-shot scrape CLI: ``culturasp-scrape [--source sala-sp] [--max N]``."""

from __future__ import annotations

import argparse
import asyncio

from culturasp.core.config import get_settings
from culturasp.core.logging import get_logger
from culturasp.db.provider import get_repository
from culturasp.db.session import create_all
from culturasp.scraper.parsers import PARSERS
from culturasp.scraper.pipeline import ScrapePipeline

logger = get_logger(__name__)

#: Per-source listing (programme) URL. Discovered links are scraped from here.
LISTING_PATHS = {
    "sala-sp": "/salasp/pt/programacao",
}


async def _run(source: str, max_events: int | None) -> int:
    settings = get_settings()
    parser = PARSERS[source]
    repo = get_repository()
    create_all()  # dev convenience; prod uses Alembic

    listing_url = settings.sala_sp_base_url + LISTING_PATHS[source]
    pipeline = ScrapePipeline(parser, repo)
    events = await pipeline.run(listing_url, max_events=max_events)
    logger.info("cli_done", source=source, events=len(events))
    return len(events)


def main() -> None:
    ap = argparse.ArgumentParser(description="CulturaSP-Adapter one-shot scraper")
    ap.add_argument("--source", default="sala-sp", choices=sorted(PARSERS))
    ap.add_argument("--max", type=int, default=None, help="Limit number of events")
    args = ap.parse_args()
    count = asyncio.run(_run(args.source, args.max))
    print(f"Scraped {count} events from {args.source}")


if __name__ == "__main__":
    main()
