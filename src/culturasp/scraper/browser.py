"""Playwright browser helper.

A thin async context manager that yields a Chromium page with an identifiable
User-Agent. Kept separate from the fetcher so that politeness logic (robots,
delay, cache) lives in one place and rendering lives in another.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from culturasp.core.config import get_settings


@asynccontextmanager
async def browser_context() -> AsyncIterator[BrowserContext]:
    """Yield a Playwright BrowserContext with our identifiable UA.

    Cookies persist across pages within the same context (one batch run), then
    the context is discarded. No login, no personal data.
    """
    settings = get_settings()
    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        context: BrowserContext = await browser.new_context(
            user_agent=settings.user_agent,
            locale="pt-BR",
        )
        try:
            yield context
        finally:
            await context.close()
            await browser.close()


async def render_html(
    context: BrowserContext, url: str, *, wait_selector: str | None = None
) -> str:
    """Open ``url`` in a new page, wait for it to settle, return the HTML."""
    page: Page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle")
        if wait_selector:
            await page.wait_for_selector(wait_selector, timeout=10_000)
        return await page.content()
    finally:
        await page.close()
