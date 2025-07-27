"""
핫딜 크롤러를 위한 데이터 모델.
"""

from datetime import datetime
from typing import Optional


class HotDealItem:
    """핫딜 아이템을 나타내는 클래스."""
    
    def __init__(self, idx: str, title: str, url: str, price: Optional[str] = None,
                 timestamp: Optional[datetime] = None, site: str = "", 
                 category: Optional[str] = None):
        """
        핫딜 아이템을 초기화합니다.
        
        Args:
            idx: 핫딜 아이템의 고유 인덱스
            title: 핫딜의 제목
            url: 핫딜의 URL
            price: 아이템의 가격 (선택 사항)
            timestamp: 딜이 게시된 시간 (선택 사항)
            site: 딜이 발견된 사이트의 이름 (선택 사항)
            category: 딜의 카테고리 (선택 사항)
        """
        self.idx = idx
        self.title = title
        self.url = url
        self.price = price
        self.timestamp = timestamp or datetime.now()
        self.site = site
        self.category = category

    def __str__(self) -> str:
        """핫딜 아이템의 문자열 표현을 반환합니다."""
        return f"[{self.site}] {self.title} - {self.price or 'N/A'} ({self.url})"