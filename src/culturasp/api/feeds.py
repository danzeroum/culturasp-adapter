"""iCal and RSS rendering for the event list — open distribution formats."""

from __future__ import annotations

from culturasp.models.event import CulturalEvent


def events_to_ical(events: list[CulturalEvent]) -> str:
    """Render events as an iCalendar (VCALENDAR) document."""
    from ics import Calendar, Event

    cal = Calendar()
    for e in events:
        ev = Event()
        ev.name = e.title
        ev.uid = e.id
        ev.location = e.venue
        ev.url = str(e.source_url)
        if e.start:
            ev.begin = e.start
        if e.end:
            ev.end = e.end
        description = []
        if e.conductor:
            description.append(f"Regente: {e.conductor}")
        if e.program:
            description.append(
                "Programa: "
                + "; ".join(f"{p.composer or ''} {p.work or ''}".strip() for p in e.program)
            )
        ev.description = "\n".join(description) or None
        cal.events.add(ev)
    return cal.serialize()


def events_to_rss(events: list[CulturalEvent]) -> bytes:
    """Render events as an RSS 2.0 feed."""
    from feedgen.feed import FeedGenerator

    fg = FeedGenerator()
    fg.title("CulturaSP-Adapter — Eventos")
    fg.link(href="https://github.com/danzeroum/culturasp-adapter", rel="alternate")
    fg.description("Eventos culturais públicos de São Paulo, estruturados em dados abertos.")
    fg.language("pt-BR")
    for e in events:
        fe = fg.add_entry()
        fe.id(e.id)
        fe.title(e.title)
        fe.link(href=str(e.source_url))
        if e.start:
            fe.pubDate(e.start)
        fe.description(f"{e.venue} — {e.start.isoformat() if e.start else 'data a confirmar'}")
    return fg.rss_str(pretty=True)
