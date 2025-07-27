"""
핫딜 크롤러를 위한 기본 크롤러 모듈.

이 모듈은 모든 사이트별 크롤러를 위한 추상 기본 클래스를 제공합니다.
"""

import abc
import logging
import time
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from .models import HotDealItem


class BaseCrawler(abc.ABC):
    """모든 사이트별 크롤러를 위한 추상 기본 클래스."""
    
    def __init__(self, site_name: str, base_url: str):
        """
        기본 크롤러를 초기화합니다.
        
        Args:
            site_name: 사이트 이름
            base_url: 사이트의 기본 URL
        """
        self.site_name = site_name
        self.base_url = base_url
        self.logger = logging.getLogger(f"{__name__}.{self.site_name}")
        self.driver = None
        
    def _setup_driver(self):
        """Selenium WebDriver를 설정합니다."""
        if self.driver is not None:
            return
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)  # 페이지 로드 타임아웃 설정

            self.logger.info(f"WebDriver set up for {self.site_name}")
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def _close_driver(self):
        """Selenium WebDriver를 종료합니다."""
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info(f"WebDriver closed for {self.site_name}")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
    
    def get_page(self, url: str) -> bool:
        """
        Selenium을 사용하여 페이지로 이동합니다.
        
        Args:
            url: 이동할 URL
            
        Returns:
            bool: 이동이 성공하면 True, 그렇지 않으면 False
        """
        if self.driver is None:
            self._setup_driver()
            
        try:
            self.driver.get(url)
            # 페이지 로딩 대기
            time.sleep(2)
            return True
        except WebDriverException as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=10):
        """
        페이지에 요소가 나타날 때까지 대기합니다.
        
        Args:
            by: 요소를 찾는 방법 (예: By.ID, By.CSS_SELECTOR)
            value: 검색할 값
            timeout: 최대 대기 시간(초)
            
        Returns:
            요소를 찾으면 해당 요소, 찾지 못하면 None
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element {by}={value}")
            return None
    
    def wait_for_elements(self, by, value, timeout=10):
        """
        페이지에 요소들이 나타날 때까지 대기합니다.
        
        Args:
            by: 요소들을 찾는 방법 (예: By.ID, By.CSS_SELECTOR)
            value: 검색할 값
            timeout: 최대 대기 시간(초)
            
        Returns:
            요소들을 찾으면 해당 요소들, 찾지 못하면 빈 리스트
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for elements {by}={value}")
            return []
    
    @abc.abstractmethod
    def crawl(self) -> List[HotDealItem]:
        """
        사이트를 크롤링하고 핫딜 아이템 목록을 반환합니다.
        
        Returns:
            List[HotDealItem]: 핫딜 아이템 목록
        """
        pass
    
    def __del__(self):
        """WebDriver가 확실히 종료되도록 하는 소멸자."""
        self._close_driver()