"""Template for a new source parser. Copy this file to ``<source>.py``.

This is a STARTING POINT, not a working parser — it is intentionally NOT
registered in ``parsers/__init__.py``. Steps to add a real source:

1. Copy this file to ``parsers/<source>.py`` and rename the class.
2. Set ``source`` to a stable slug (e.g. ``"pinacoteca"``).
3. Capture real snapshots with ``scripts/capture_fixture.py`` (run locally) and
   implement the selectors against them — never hardcode invented URLs.
4. Register the parser in ``parsers/__init__.py`` (the ``PARSERS`` dict) and add
   its listing path to ``LISTING_PATHS`` in ``scraper/cli.py``.
5. Add offline unit tests using the captured fixtures (see
   ``tests/unit/test_sala_sp_parser.py`` for the pattern).

See ``parsers/sala_sp.py`` for a complete, label-based reference implementation.
"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

from culturasp.core.exceptions import ParseError
from culturasp.models.event import CulturalEvent
from culturasp.scraper.parsers.base import BaseParser


class TemplateParser(BaseParser):
    #: TODO: set a stable slug, e.g. "pinacoteca".
    source = "template"

    #: TODO: the host this parser handles.
    _host = "example.org"

    def can_parse(self, url: str) -> bool:
        return self._host in urlparse(url).netloc

    def list_event_urls(self, listing_html: str, base_url: str) -> list[str]:
        # TODO: parse the rendered listing page and return the discovered event
        # URLs (absolute). Discover them — do not hardcode/invent URLs.
        raise NotImplementedError("implement list_event_urls for this source")

    def parse_event(self, html: str, url: str, *, scraped_at: datetime) -> CulturalEvent:
        # TODO: extract fields by label (resilient to layout), build and return a
        # CulturalEvent. Raise ParseError when the page has no usable event.
        raise ParseError("TemplateParser is not implemented")

    def anchor_selectors(self) -> list[str]:
        # TODO: selectors that define "the layout we expect" (used by the monitor).
        return ["h1"]
