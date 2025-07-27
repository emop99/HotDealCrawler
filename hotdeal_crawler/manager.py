"""
핫딜 크롤러를 위한 크롤러 관리자 모듈.

이 모듈은 여러 크롤러를 병렬로 조율하기 위한 관리자 클래스를 제공합니다.
"""

import logging
import threading
import time
import concurrent.futures
from typing import List

from .base_crawler import BaseCrawler
from .models import HotDealItem

logger = logging.getLogger(__name__)


class HotDealCrawlerManager:
    """여러 크롤러를 병렬로 조율하기 위한 관리자 클래스."""
    
    def __init__(self):
        """크롤러 관리자를 초기화합니다."""
        self.crawlers = []
        self.results = []
        self.lock = threading.Lock()
    
    def add_crawler(self, crawler: BaseCrawler):
        """
        관리자에 크롤러를 추가합니다.
        
        Args:
            crawler: 추가할 크롤러
        """
        self.crawlers.append(crawler)
    
    def _crawl_site(self, crawler: BaseCrawler):
        """
        사이트를 크롤링하고 결과를 저장합니다.
        
        Args:
            crawler: 사용할 크롤러
        """
        try:
            deals = crawler.crawl()
            with self.lock:
                self.results.extend(deals)
        except Exception as e:
            logger.error(f"크롤러 {crawler.site_name}에서 오류 발생: {e}")
    
    def crawl_all(self, max_workers: int = None) -> List[HotDealItem]:
        """
        ThreadPoolExecutor를 사용하여 모든 사이트를 병렬로 크롤링합니다.
        
        Args:
            max_workers: 사용할 최대 작업자 스레드 수
                         (기본값: 크롤러 수)
        
        Returns:
            List[HotDealItem]: 발견된 모든 핫딜 아이템 목록
        """
        self.results = []
        start_time = time.time()
        
        # If max_workers is not specified, use the number of crawlers
        if max_workers is None:
            max_workers = len(self.crawlers)
        
        logger.info(f"{max_workers}개의 작업자로 병렬 크롤링을 시작합니다")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._crawl_site, crawler) for crawler in self.crawlers]
            concurrent.futures.wait(futures)
        
        elapsed_time = time.time() - start_time
        logger.info(f"크롤링이 {elapsed_time:.2f}초 만에 완료되었습니다")
        logger.info(f"총 {len(self.results)}개의 딜을 찾았습니다")
        
        return self.results