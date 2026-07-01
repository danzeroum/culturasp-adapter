"""Map :class:`CulturalEvent` to schema.org JSON-LD.

This is the open-data contract consumers rely on. We keep the mapping in one
place so the schema.org shape can evolve independently of the internal model.
The ``@type`` follows ``event.schema_type`` (MusicEvent / ExhibitionEvent /
Event); music-specific properties are emitted only for ``MusicEvent``.
Reference: https://schema.org/Event
"""

from __future__ import annotations

from typing import Any

from culturasp.models.event import CulturalEvent, SchemaType

SCHEMA_CONTEXT = "https://schema.org"

#: Venue @type per event type — music halls are MusicVenue; everything else Place.
_VENUE_TYPE = {SchemaType.music_event: "MusicVenue"}


def event_to_jsonld(event: CulturalEvent) -> dict[str, Any]:
    """Render a single event as a schema.org JSON-LD document.

    The top-level ``@type`` is driven by ``event.schema_type`` so non-music
    sources (e.g. museum exhibitions) map to the right schema.org class.
    """
    doc: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": event.schema_type.value,
        "@id": str(event.source_url),
        "name": event.title,
        "url": str(event.source_url),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": _VENUE_TYPE.get(event.schema_type, "Place"),
            "name": event.venue,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "São Paulo",
                "addressRegion": "SP",
                "addressCountry": "BR",
            },
        },
    }

    # Audience / age suitability — schema.org Event.typicalAgeRange + audience.
    age_range = event.age_range_text
    if age_range:
        doc["typicalAgeRange"] = age_range
    if event.audience or event.min_age is not None or event.max_age is not None:
        audience: dict[str, Any] = {"@type": "PeopleAudience"}
        if event.audience:
            audience["audienceType"] = event.audience
        if event.min_age is not None:
            audience["suggestedMinAge"] = event.min_age
        if event.max_age is not None:
            audience["suggestedMaxAge"] = event.max_age
        doc["audience"] = audience

    if event.start:
        doc["startDate"] = event.start.isoformat()
    if event.end:
        doc["endDate"] = event.end.isoformat()
    if event.duration_minutes:
        # ISO 8601 duration
        doc["duration"] = f"PT{event.duration_minutes}M"

    for performer in event.performers:
        doc.setdefault("performer", []).append({"@type": "Person", "name": performer})

    # Music-specific properties only make sense for a MusicEvent.
    if event.schema_type is SchemaType.music_event:
        if event.conductor:
            doc.setdefault("performer", []).insert(
                0, {"@type": "Person", "name": event.conductor, "roleName": "conductor"}
            )
        if event.program:
            doc["workPerformed"] = [
                {
                    "@type": "MusicComposition",
                    "name": item.work,
                    **(
                        {"composer": {"@type": "Person", "name": item.composer}}
                        if item.composer
                        else {}
                    ),
                }
                for item in event.program
                if item.work or item.composer
            ]

    # Offers — free tickets are price "0". Descriptive only.
    offer: dict[str, Any] = {
        "@type": "Offer",
        "price": "0" if event.ticket.free_of_charge else None,
        "priceCurrency": "BRL",
        "availability": "https://schema.org/InStock",
    }
    if event.ticket.external_url:
        offer["url"] = str(event.ticket.external_url)
    doc["offers"] = {k: v for k, v in offer.items() if v is not None}
    doc["isAccessibleForFree"] = event.ticket.free_of_charge

    # Accessibility — schema.org accessibility properties.
    acc = event.accessibility
    features: list[str] = []
    if acc.sign_language:
        features.append("signLanguageInterpretation")
    if acc.audio_description:
        features.append("audioDescription")
    if (acc.wheelchair_seats or 0) > 0:
        features.append("wheelchairAccessibleSeating")
    if features:
        doc["accessibilityFeature"] = features
    if acc.notes:
        doc["accessibilitySummary"] = acc.notes

    return doc
