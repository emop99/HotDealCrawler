"""
Site-specific crawler implementations.

This package contains crawler implementations for specific community websites.
"""

from .ruliweb_crawler import RuliwebCrawler
from .coolenjoy_crawler import CoolenjoyCrawler
from .ppomppu_crawler import PPomppuCrawler

__all__ = [
    'RuliwebCrawler',
    'CoolenjoyCrawler',
    'PPomppuCrawler',
]