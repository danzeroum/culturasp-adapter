"""Periodic collection scheduler (the ``scraper`` Docker service entrypoint).

Runs a polite scrape of every registered source on a fixed interval. Kept thin:
all real work lives in :class:`ScrapePipeline`.
"""

from __future__ import annotations

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from culturasp.core.config import get_settings
from culturasp.core.logging import get_logger
from culturasp.db.provider import get_repository
from culturasp.db.session import create_all
from culturasp.scraper.cli import listing_url
from culturasp.scraper.parsers import PARSERS
from culturasp.scraper.pipeline import ScrapePipeline

logger = get_logger(__name__)


async def collect_all() -> None:
    settings = get_settings()
    repo = get_repository()
    for source, parser in PARSERS.items():
        try:
            await ScrapePipeline(parser, repo).run(listing_url(source, settings))
        except Exception as exc:
            logger.error("source_collection_failed", source=source, error=str(exc))


async def _main() -> None:
    settings = get_settings()
    create_all()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(collect_all, "interval", seconds=settings.scrape_interval, max_instances=1)
    scheduler.start()
    logger.info("scheduler_started", interval=settings.scrape_interval)
    await collect_all()  # run once immediately on boot
    while True:  # keep the event loop alive
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(_main())
