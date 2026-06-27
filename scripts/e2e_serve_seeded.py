"""Boot the real FastAPI app with an in-memory repo seeded with one event.

Used by the frontend Playwright smoke test (frontend/e2e) so the SPA can be
driven against the real API surface without Postgres/Redis. Mirrors the seed in
tests/integration/test_api.py, but with richer fields (end time, audio
description, ticket external_url) so the Detail screen's accessibility rows and
the "leave" modal have data to render.

Run: python scripts/e2e_serve_seeded.py  (serves on http://127.0.0.1:8000)
"""

from __future__ import annotations

from datetime import datetime, timezone

import uvicorn

from culturasp.api.deps import get_event_repository
from culturasp.api.main import app
from culturasp.db.repository import InMemoryEventRepository
from culturasp.models.accessibility import AccessibilityInfo
from culturasp.models.event import CulturalEvent, ProgramItem, SchemaType, TicketPolicy


def build_repo() -> InMemoryEventRepository:
    repo = InMemoryEventRepository()
    repo.upsert(
        CulturalEvent(
            id="sala-sp:1727",
            source="sala-sp",
            source_url="https://salasaopaulo.art.br/salasp/pt/concerto/1727",
            title="Orquestra Antares — Matinais",
            start=datetime(2026, 8, 8, 10, 50, tzinfo=timezone.utc),
            end=datetime(2026, 8, 8, 11, 50, tzinfo=timezone.utc),
            duration_minutes=60,
            schema_type=SchemaType.music_event,
            venue="Sala São Paulo",
            program=[
                ProgramItem(composer="Mozart", work="Sinfonia nº 40"),
                ProgramItem(composer="Händel", work="Water Music"),
            ],
            conductor="Fábio Prado",
            performers=["Orquestra Antares"],
            accessibility=AccessibilityInfo(
                sign_language=True,
                audio_description=True,
                wheelchair_seats=15,
                obese_seats=14,
                notes="Audiodescrição mediante reserva.",
            ),
            ticket=TicketPolicy(
                free_of_charge=True,
                distribution_window="a partir das 12h, 3 dias antes",
                cancellation_window="até 48h antes",
                external_url="https://ingressos.salasaopaulo.art.br/evento/1727",
            ),
            scraped_at=datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc),
        )
    )
    repo.set_layout_signature("sala-sp", "deadbeef")
    return repo


app.dependency_overrides[get_event_repository] = lambda: build_repo()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
