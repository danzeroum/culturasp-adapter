"""Playwright browser helper.

A thin async context manager that yields a Chromium page with an identifiable
User-Agent. Kept separate from the fetcher so that politeness logic (robots,
delay, cache) lives in one place and rendering lives in another.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal, cast
from urllib.parse import urlsplit

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    ProxySettings,
    async_playwright,
)

from culturasp.core.config import get_settings

WaitUntil = Literal["commit", "domcontentloaded", "load", "networkidle"]


def proxy_settings(proxy_url: str) -> ProxySettings | None:
    """Translate a ``scheme://user:pass@host:port`` URL into Playwright proxy
    settings. Returns ``None`` for an empty/invalid value (direct connection)."""
    proxy_url = proxy_url.strip()
    if not proxy_url:
        return None
    parts = urlsplit(proxy_url)
    if not parts.hostname:
        return None
    server = f"{parts.scheme or 'http'}://{parts.hostname}"
    if parts.port:
        server = f"{server}:{parts.port}"
    proxy: ProxySettings = {"server": server}
    if parts.username:
        proxy["username"] = parts.username
    if parts.password:
        proxy["password"] = parts.password
    return proxy


@asynccontextmanager
async def browser_context() -> AsyncIterator[BrowserContext]:
    """Yield a Playwright BrowserContext with our identifiable UA.

    Cookies persist across pages within the same context (one batch run), then
    the context is discarded. No login, no personal data. Routes through an
    outbound proxy when ``CULTURASP_HTTP_PROXY`` is set.
    """
    settings = get_settings()
    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(
            headless=True, proxy=proxy_settings(settings.http_proxy)
        )
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
    """Open ``url`` in a new page, wait for it to settle, return the HTML.

    The load strategy and timeout come from settings (``nav_wait_until`` /
    ``nav_timeout_ms``) so fragile-but-default ``networkidle`` can be avoided.
    """
    settings = get_settings()
    page: Page = await context.new_page()
    try:
        await page.goto(
            url,
            wait_until=cast(WaitUntil, settings.nav_wait_until),
            timeout=settings.nav_timeout_ms,
        )
        if wait_selector:
            await page.wait_for_selector(wait_selector, timeout=settings.nav_timeout_ms)
        return await page.content()
    finally:
        await page.close()
