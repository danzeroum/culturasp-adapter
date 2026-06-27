"""Unit tests for layout-change detection."""

from __future__ import annotations

from culturasp.scraper import monitoring
from culturasp.scraper.parsers.sala_sp import SalaSPParser


def test_signature_stable(concert_html: str) -> None:
    parser = SalaSPParser()
    sig1 = monitoring.layout_signature(concert_html, parser)
    sig2 = monitoring.layout_signature(concert_html, parser)
    assert sig1 == sig2


def test_no_change_when_signature_matches(concert_html: str) -> None:
    parser = SalaSPParser()
    sig = monitoring.layout_signature(concert_html, parser)
    assert monitoring.detect_change(concert_html, parser, sig) is False


def test_change_detected_when_anchors_differ(concert_html: str) -> None:
    parser = SalaSPParser()
    # Mutate the layout: drop all <h2> anchors -> signature must change.
    mutated = concert_html.replace("<h2>", "<div>").replace("</h2>", "</div>")
    previous = monitoring.layout_signature(concert_html, parser)
    assert monitoring.detect_change(mutated, parser, previous) is True
