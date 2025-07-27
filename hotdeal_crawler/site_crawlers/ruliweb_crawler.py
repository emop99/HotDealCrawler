"""
루리웹 사이트 크롤러 구현.
"""

import logging
import re
from typing import List

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ..base_crawler import BaseCrawler
from ..models import HotDealItem


class RuliwebCrawler(BaseCrawler):
    """루리웹 커뮤니티 사이트용 크롤러."""
    
    def __init__(self):
        """루리웹 크롤러를 초기화합니다."""
        super().__init__("Ruliweb", "https://bbs.ruliweb.com")
        self.hot_deal_url = f"{self.base_url}/market/board/1020"
        self.logger = logging.getLogger(f"{__name__}.{self.site_name}")
    
    def crawl(self) -> List[HotDealItem]:
        """
        루리웹 사이트에서 핫딜 정보를 크롤링합니다.
        
        Returns:
            List[HotDealItem]: 핫딜 아이템 목록
        """
        self.logger.info(f"{self.site_name}에서 핫딜 크롤링 중")
        deals = []
        
        # 핫딜 페이지로 이동
        if not self.get_page(self.hot_deal_url):
            self.logger.error(f"{self.hot_deal_url}로 이동하지 못했습니다")
            return deals
        
        try:
            # 모든 딜 아이템 찾기
            deal_elements = self.driver.find_elements(By.CSS_SELECTOR, 'tr.table_body')
            
            for element in deal_elements:
                try:
                    # 카테고리 추출
                    try:
                        category_element = element.find_element(By.CSS_SELECTOR, 'td.divsn')
                        category = category_element.text.strip()
                    except NoSuchElementException:
                        category = None

                    if category == "업체핫딜" or category == "BEST" or category == '공지':
                        continue

                    # 제목 추출
                    title_element = element.find_element(By.CSS_SELECTOR, 'a.deco')
                    title = title_element.text.strip()

                    # 제목에 댓글 개수 제거
                    # 예: "제목 (댓글수)" 형식에서 댓글 수를 제거
                    title = re.sub(r'\s*\(\d+\)$', '', title)  # 댓글 수 제거

                    # URL 추출
                    url = title_element.get_attribute('href')

                    # idx 추출
                    idx_element = element.find_element(By.CSS_SELECTOR, 'td.id')
                    idx = idx_element.text.strip()

                    deals.append(HotDealItem(
                        idx=idx,
                        title=title,
                        url=url,
                        category=category,
                        site=self.site_name
                    ))
                except Exception as e:
                    self.logger.error(f"딜 아이템 파싱 오류: {e}")
            
        except Exception as e:
            self.logger.error(f"{self.site_name} 크롤링 오류: {e}")
        finally:
            self._close_driver()
        
        self.logger.info(f"{self.site_name}에서 {len(deals)}개의 딜을 찾았습니다")
        return deals