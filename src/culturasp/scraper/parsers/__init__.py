from culturasp.scraper.parsers.base import BaseParser
from culturasp.scraper.parsers.sala_sp import SalaSPParser

#: Registry of available source parsers, keyed by source slug.
PARSERS: dict[str, BaseParser] = {
    SalaSPParser.source: SalaSPParser(),
}

__all__ = ["PARSERS", "BaseParser", "SalaSPParser"]
