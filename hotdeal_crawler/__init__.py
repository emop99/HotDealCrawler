"""
핫딜 크롤러 패키지.

이 패키지는 다양한 한국 커뮤니티 웹사이트에서 핫딜을 크롤링하는 기능을 제공합니다.
"""

from .models import HotDealItem
from .base_crawler import BaseCrawler
from .manager import HotDealCrawlerManager

# 사이트별 크롤러 가져오기
from .site_crawlers.ruliweb_crawler import RuliwebCrawler

__all__ = [
    'HotDealItem',
    'BaseCrawler',
    'HotDealCrawlerManager',
    'RuliwebCrawler',
]