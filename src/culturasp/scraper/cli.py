"""One-shot scrape CLI: ``culturasp-scrape [--source sala-sp] [--max N]``."""

from __future__ import annotations

import argparse
import asyncio

from culturasp.core.config import Settings, get_settings
from culturasp.core.logging import get_logger
from culturasp.db.provider import get_repository
from culturasp.db.session import create_all
from culturasp.scraper.parsers import PARSERS
from culturasp.scraper.pipeline import ScrapePipeline

logger = get_logger(__name__)

#: Per-source listing (programme) path. Discovered links are scraped from here.
#: For sala-sp we use the ticketing programme ("programacao-ingressos"): it
#: renders the full season (~35 concerts) into the DOM, whereas "/programacao"
#: only shows the next few ("Próximos concertos"). For sesc-sp we seed the
#: children's programme listing.
LISTING_PATHS = {
    "sala-sp": "/salasp/pt/programacao-ingressos",
    "sesc-sp": "/programacao/infantil/",
}

#: Which configured base URL each source's listing path is joined onto. Lets one
#: scheduler serve sources on different hosts (Sala SP, SESC, ...).
SOURCE_BASE_URL_ATTR = {
    "sala-sp": "sala_sp_base_url",
    "sesc-sp": "sesc_base_url",
}


def listing_url(source: str, settings: Settings) -> str:
    """Resolve a source's absolute listing URL from its configured base URL."""
    base = getattr(settings, SOURCE_BASE_URL_ATTR[source])
    return base.rstrip("/") + LISTING_PATHS[source]


async def _run(source: str, max_events: int | None) -> int:
    settings = get_settings()
    parser = PARSERS[source]
    repo = get_repository()
    create_all()  # dev convenience; prod uses Alembic

    pipeline = ScrapePipeline(parser, repo)
    events = await pipeline.run(listing_url(source, settings), max_events=max_events)
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
