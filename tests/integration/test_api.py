"""API tests using an in-memory repository (no Postgres/Redis needed).

The repository dependency is overridden so the whole API surface can be tested
offline and deterministically.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from culturasp.api.deps import get_event_repository
from culturasp.api.main import app
from culturasp.db.repository import InMemoryEventRepository
from culturasp.models.accessibility import AccessibilityInfo
from culturasp.models.event import CulturalEvent, ProgramItem, SchemaType, TicketPolicy

NOW = datetime(2026, 6, 27, tzinfo=timezone.utc)


def _seed() -> InMemoryEventRepository:
    repo = InMemoryEventRepository()
    repo.upsert(
        CulturalEvent(
            id="sala-sp:1727",
            source="sala-sp",
            source_url="https://salasaopaulo.art.br/salasp/pt/concerto/1727",
            title="Orquestra Antares",
            start=datetime(2026, 8, 8, 10, 50, tzinfo=timezone.utc),
            duration_minutes=60,
            conductor="Fábio Prado",
            program=[ProgramItem(composer="Mozart", work="Sinfonia nº 40")],
            accessibility=AccessibilityInfo(sign_language=True, wheelchair_seats=15),
            ticket=TicketPolicy(free_of_charge=True),
            scraped_at=NOW,
        )
    )
    repo.upsert(
        CulturalEvent(
            id="sesc:o-pequeno-principe",
            source="sesc",
            source_url="https://www.sescsp.org.br/programacao/o-pequeno-principe",
            title="O Pequeno Príncipe",
            schema_type=SchemaType.childrens_event,
            start=datetime(2026, 8, 9, 15, 0, tzinfo=timezone.utc),
            venue="Pompeia",
            min_age=4,
            max_age=10,
            audience="infantil",
            category="teatro",
            ticket=TicketPolicy(free_of_charge=True),
            scraped_at=NOW,
        )
    )
    repo.set_layout_signature("sala-sp", "deadbeef")
    return repo


@pytest.fixture
def client() -> TestClient:
    repo = _seed()
    app.dependency_overrides[get_event_repository] = lambda: repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_list_events(client: TestClient) -> None:
    resp = client.get("/v1/events")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    titles = {e["title"] for e in data}
    assert titles == {"Orquestra Antares", "O Pequeno Príncipe"}


def test_filter_by_source(client: TestClient) -> None:
    assert len(client.get("/v1/events?source=sala-sp").json()) == 1
    assert client.get("/v1/events?source=nonexistent").json() == []


def test_filter_by_audience(client: TestClient) -> None:
    data = client.get("/v1/events?audience=infantil").json()
    assert len(data) == 1
    assert data[0]["id"] == "sesc:o-pequeno-principe"


def test_filter_by_age(client: TestClient) -> None:
    # 6 falls inside the 4-10 band -> matches the children's event only.
    six = client.get("/v1/events?age=6").json()
    assert [e["id"] for e in six] == ["sesc:o-pequeno-principe"]
    # 30 is outside every published band; the concert has no band → no match.
    assert client.get("/v1/events?age=30").json() == []


def test_childrens_event_jsonld_age_fields(client: TestClient) -> None:
    doc = client.get("/v1/events/sesc:o-pequeno-principe/jsonld").json()
    assert doc["@type"] == "ChildrensEvent"
    assert doc["typicalAgeRange"] == "4-10"
    assert doc["audience"]["suggestedMinAge"] == 4


def test_event_detail_and_404(client: TestClient) -> None:
    assert client.get("/v1/events/sala-sp:1727").json()["conductor"] == "Fábio Prado"
    assert client.get("/v1/events/sala-sp:9999").status_code == 404


def test_event_jsonld(client: TestClient) -> None:
    doc = client.get("/v1/events/sala-sp:1727/jsonld").json()
    assert doc["@type"] == "MusicEvent"
    assert doc["duration"] == "PT60M"


def test_accessibility_filter(client: TestClient) -> None:
    assert len(client.get("/v1/accessibility?feature=libras").json()) == 1
    assert client.get("/v1/accessibility?feature=audio_description").json() == []


def test_schema_endpoint(client: TestClient) -> None:
    body = client.get("/v1/schema").json()
    assert body["jsonld_type"] == "MusicEvent"
    assert "json_schema" in body


def test_sources(client: TestClient) -> None:
    sources = client.get("/v1/sources").json()
    assert sources[0]["source"] == "sala-sp"
    assert sources[0]["layout_signature"] == "deadbeef"


def test_ical_feed(client: TestClient) -> None:
    resp = client.get("/v1/events.ics")
    assert resp.status_code == 200
    assert "BEGIN:VCALENDAR" in resp.text
