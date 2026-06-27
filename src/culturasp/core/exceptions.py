"""Domain-level exceptions for the adapter."""

from __future__ import annotations


class CulturaSPError(Exception):
    """Base class for all adapter errors."""


class RobotsDisallowedError(CulturaSPError):
    """Raised when robots.txt forbids fetching a URL."""


class ParseError(CulturaSPError):
    """Raised when a parser cannot extract a valid event from a page."""


class LayoutChangedError(CulturaSPError):
    """Raised/used by the monitor when the source layout no longer matches."""
