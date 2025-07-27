"""
핫딜 크롤러의 메인 모듈.

이 모듈은 핫딜 크롤러 애플리케이션의 진입점을 제공합니다.
"""

import argparse
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from hotdeal_crawler import (
    HotDealCrawlerManager,
    PPomppuCrawler,
    RuliwebCrawler,
    CoolenjoyCrawler,
    HotDealItem
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 사이트 이름과 크롤러 클래스의 매핑
SITE_CRAWLERS = {
    "ppomppu": PPomppuCrawler,
    "ruliweb": RuliwebCrawler,
    "coolenjoy": CoolenjoyCrawler
}

# 결과 저장 디렉토리
RESULT_DIR = "result"


def save_to_json(deals: List[HotDealItem], site_name: str = None):
    """
    크롤링한 핫딜 정보를 JSON 파일로 저장합니다.
    
    Args:
        deals: 저장할 핫딜 목록
        site_name: 사이트 이름 (None인 경우 모든 사이트를 하나의 파일로 저장)
    """
    # 결과 디렉토리가 없으면 생성
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
        logger.info(f"결과 디렉토리 생성: {RESULT_DIR}")
    
    # 파일명 생성 (사이트명_날짜시간.json 또는 all_날짜시간.json)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{site_name or 'all'}_{timestamp}.json"
    filepath = os.path.join(RESULT_DIR, filename)
    
    # HotDealItem 객체를 딕셔너리로 변환
    deals_dict = []
    for deal in deals:
        deal_dict = {
            "idx": deal.idx,
            "title": deal.title,
            "url": deal.url,
            "price": deal.price,
            "timestamp": deal.timestamp.isoformat(),
            "site": deal.site,
            "category": deal.category
        }
        deals_dict.append(deal_dict)
    
    # JSON 파일로 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(deals_dict, f, ensure_ascii=False, indent=2)
    
    logger.info(f"{len(deals)}개의 핫딜 정보를 {filepath}에 저장했습니다.")


def main():
    """핫딜 크롤러를 실행하는 메인 함수."""
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="핫딜 크롤러")
    parser.add_argument(
        "--sites", 
        nargs="+", 
        choices=SITE_CRAWLERS.keys(),
        help="크롤링할 사이트 목록 (지정하지 않으면 모든 사이트 크롤링)"
    )
    args = parser.parse_args()
    
    logger.info("핫딜 크롤러 시작")
    
    # 크롤러 매니저 생성
    manager = HotDealCrawlerManager()
    
    # 사이트별 크롤러 추가
    if args.sites:
        # 지정된 사이트만 크롤링
        for site in args.sites:
            crawler_class = SITE_CRAWLERS[site]
            manager.add_crawler(crawler_class())
            logger.info(f"{site} 크롤러 추가")
    else:
        # 모든 사이트 크롤링
        for site, crawler_class in SITE_CRAWLERS.items():
            manager.add_crawler(crawler_class())
            logger.info(f"{site} 크롤러 추가")
    
    # 사이트를 병렬로 크롤링
    deals = manager.crawl_all()
    
    # 결과 출력
    print(f"\n{len(deals)}개의 핫딜을 찾았습니다:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal}")
    
    # 결과를 JSON 파일로 저장
    save_to_json(deals)
    
    # 사이트별로 결과 저장
    if len(manager.crawlers) > 1:
        site_deals = {}
        for deal in deals:
            site = deal.site.lower()
            if site not in site_deals:
                site_deals[site] = []
            site_deals[site].append(deal)
        
        for site, site_deal_list in site_deals.items():
            save_to_json(site_deal_list, site)
    
    logger.info("핫딜 크롤러 완료")


if __name__ == "__main__":
    main()