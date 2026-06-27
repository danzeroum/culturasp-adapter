"""/v1/schema — the open-data contract (JSON Schema + JSON-LD context)."""

from __future__ import annotations

from fastapi import APIRouter

from culturasp.models.event import CulturalEvent
from culturasp.models.jsonld import SCHEMA_CONTEXT

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("")
def get_schema() -> dict:
    """Return the JSON Schema of CulturalEvent and the schema.org context used."""
    return {
        "json_schema": CulturalEvent.model_json_schema(),
        "jsonld_context": SCHEMA_CONTEXT,
        "jsonld_type": "MusicEvent",
    }
