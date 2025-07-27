"""
뽐뿌 사이트 크롤러 구현.
"""

import logging
from typing import List

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ..base_crawler import BaseCrawler
from ..models import HotDealItem


class PPomppuCrawler(BaseCrawler):
    """뽐뿌 커뮤니티 사이트용 크롤러."""
    
    def __init__(self):
        """뽐뿌 크롤러를 초기화합니다."""
        super().__init__("Ppomppu", "https://www.ppomppu.co.kr/")
        self.hot_deal_url = f"{self.base_url}/zboard/zboard.php?id=ppomppu"
        self.logger = logging.getLogger(f"{__name__}.{self.site_name}")

    def crawl(self) -> List[HotDealItem]:
        """
        뽐뿌 사이트에서 핫딜 정보를 크롤링합니다.
        
        Returns:
            List[HotDealItem]: 핫딜 아이템 목록
        """
        self.logger.info(f"{self.site_name}에서 핫딜 크롤링 중")
        deals = []
        
        if not self.get_page(self.hot_deal_url):
            self.logger.error(f"{self.hot_deal_url}로 이동하지 못했습니다")
            return deals
        
        try:
            deal_elements = self.driver.find_elements(By.CSS_SELECTOR, '#revolution_main_table tbody tr.baseList')
            
            for element in deal_elements:
                try:
                    # 상단 고정 게시글은 제외
                    element_class = element.get_attribute('class')
                    if 'hotpop_bg_color' in element_class:
                        continue

                    # idx 추출
                    idx_element = element.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    idx = idx_element.text.strip() if idx_element else ""

                    # 제목 추출
                    title_element = element.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a.baseList-title')
                    title = title_element.text.strip()

                    # URL 추출
                    relative_url = title_element.get_attribute('href')
                    url = relative_url if relative_url else ""

                    deals.append(HotDealItem(
                        idx=idx,
                        title=title,
                        url=url,
                        site=self.site_name
                    ))
                except Exception as e:
                    self.logger.error(f"Error parsing deal item: {e}")
            
        except Exception as e:
            self.logger.error(f"Error crawling {self.site_name}: {e}")
        finally:
            # Close the WebDriver
            self._close_driver()
        
        self.logger.info(f"Found {len(deals)} deals from {self.site_name}")
        return deals