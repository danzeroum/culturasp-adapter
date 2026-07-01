from culturasp.scraper.parsers.base import BaseParser
from culturasp.scraper.parsers.pinacoteca import PinacotecaParser
from culturasp.scraper.parsers.sala_sp import SalaSPParser
from culturasp.scraper.parsers.sesc_sp import SescSPParser

#: Live source parsers — used by the scheduler/API. Keyed by source slug.
PARSERS: dict[str, BaseParser] = {
    SalaSPParser.source: SalaSPParser(),
}

#: Experimental/candidate parsers — NOT used at runtime. Selectors unverified;
#: validate via scripts/capture_fixture.py before promoting into PARSERS.
EXPERIMENTAL_PARSERS: dict[str, BaseParser] = {
    PinacotecaParser.source: PinacotecaParser(),
    SescSPParser.source: SescSPParser(),
}

#: Union for discovery by tooling/tests (capture script, golden tests).
ALL_PARSERS: dict[str, BaseParser] = {**PARSERS, **EXPERIMENTAL_PARSERS}

__all__ = [
    "ALL_PARSERS",
    "EXPERIMENTAL_PARSERS",
    "PARSERS",
    "BaseParser",
    "PinacotecaParser",
    "SalaSPParser",
    "SescSPParser",
]
