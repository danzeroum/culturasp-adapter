"""FastAPI application entrypoint.

Serves only data already persisted by the scraper pipeline — it never scrapes
synchronously on a request, so API traffic never translates into load on the
source site.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from culturasp import __version__
from culturasp.api.v1.routes import accessibility, events, health, schema
from culturasp.core.config import get_settings
from culturasp.core.logging import configure_logging

configure_logging()
settings = get_settings()

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])

app = FastAPI(
    title="CulturaSP-Adapter API",
    version=__version__,
    description=(
        "Open, read-only API for São Paulo's public cultural events. Data is "
        "scraped ethically from official sources and structured as schema.org "
        "JSON-LD. No authentication — the data is public."
    ),
    license_info={"name": "MIT"},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# v1 routes
app.include_router(events.router, prefix="/v1")
app.include_router(accessibility.router, prefix="/v1")
app.include_router(schema.router, prefix="/v1")
app.include_router(health.router)


@app.get("/", tags=["ops"])
def root() -> dict:
    return {
        "name": "CulturaSP-Adapter",
        "version": __version__,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
