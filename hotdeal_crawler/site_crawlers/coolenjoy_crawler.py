"""
쿨엔조이 사이트 크롤러 구현.
"""

import logging
from typing import List

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ..base_crawler import BaseCrawler
from ..models import HotDealItem


class CoolenjoyCrawler(BaseCrawler):
    """쿨엔조이 커뮤니티 사이트용 크롤러."""
    
    def __init__(self):
        """쿨엔조이 크롤러를 초기화합니다."""
        super().__init__("Coolenjoy", "https://coolenjoy.net")
        self.hot_deal_url = f"{self.base_url}/bbs/jirum"
        self.logger = logging.getLogger(f"{__name__}.{self.site_name}")
    
    def crawl(self) -> List[HotDealItem]:
        """
        쿨엔조이 사이트에서 핫딜 정보를 크롤링합니다.
        
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
            deal_elements = self.driver.find_elements(By.CSS_SELECTOR, '#bo_list ul.na-table li.d-md-table-row')
            
            for element in deal_elements:
                try:
                    # 상단 고정 게시글은 제외
                    element_class = element.get_attribute('class')
                    if 'bg-light' in element_class:
                        continue

                    # 제목 추출
                    title_element = element.find_element(By.CSS_SELECTOR, 'div:nth-child(2) .na-item a')
                    title = title_element.text.strip()

                    # URL 추출
                    url = title_element.get_attribute('href')

                    # 카테고리 추출
                    category_element = element.find_element(By.CSS_SELECTOR, 'div:nth-child(1)')
                    category = category_element.text.strip() if category_element else None

                    # 가격 추출
                    price_element = element.find_element(By.CSS_SELECTOR, 'div:nth-child(3) font')
                    price = price_element.text.strip() if price_element else "N/A"

                    # idx 추출
                    idx = url.split('/')[-1].split('?')[0]  # URL에서 마지막 부분을 idx로 사용

                    # 딜 아이템 생성 및 추가
                    deals.append(HotDealItem(
                        idx=idx,
                        title=title,
                        url=url,
                        site=self.site_name,
                        category=category,
                        price=price.replace('원', '').replace(',', '').strip() if price != "N/A" else "0",
                    ))
                except Exception as e:
                    self.logger.error(f"딜 아이템 파싱 오류: {e}")
            
        except Exception as e:
            self.logger.error(f"{self.site_name} 크롤링 오류: {e}")
        finally:
            # WebDriver 종료
            self._close_driver()
        
        self.logger.info(f"{self.site_name}에서 {len(deals)}개의 딜을 찾았습니다")
        return deals