"""
Site-specific crawler implementations.

This package contains crawler implementations for specific community websites.
"""

from .ruliweb_crawler import RuliwebCrawler

__all__ = [
    'RuliwebCrawler',
]