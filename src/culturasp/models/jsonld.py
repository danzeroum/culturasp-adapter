"""Map :class:`CulturalEvent` to schema.org/MusicEvent JSON-LD.

This is the open-data contract consumers rely on. We keep the mapping in one
place so the schema.org shape can evolve independently of the internal model.
Reference: https://schema.org/MusicEvent
"""

from __future__ import annotations

from typing import Any

from culturasp.models.event import CulturalEvent

SCHEMA_CONTEXT = "https://schema.org"


def event_to_jsonld(event: CulturalEvent) -> dict[str, Any]:
    """Render a single event as a schema.org/MusicEvent JSON-LD document."""
    doc: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "MusicEvent",
        "@id": str(event.source_url),
        "name": event.title,
        "url": str(event.source_url),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": "MusicVenue",
            "name": event.venue,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "São Paulo",
                "addressRegion": "SP",
                "addressCountry": "BR",
            },
        },
    }

    if event.start:
        doc["startDate"] = event.start.isoformat()
    if event.end:
        doc["endDate"] = event.end.isoformat()
    if event.duration_minutes:
        # ISO 8601 duration
        doc["duration"] = f"PT{event.duration_minutes}M"

    if event.conductor:
        doc["performer"] = [{"@type": "Person", "name": event.conductor, "roleName": "conductor"}]
    for performer in event.performers:
        doc.setdefault("performer", []).append({"@type": "Person", "name": performer})

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
