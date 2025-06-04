import re
from datetime import datetime, timedelta
from typing import Optional
from .utils import add_months

def handle_month_day_pattern(text: str, now: datetime) -> Optional[str]:
    """월/일 패턴 매칭 (다음 달 3일, 이번 달 15일 등)"""
    pattern = r"(이번|다음)\s*달\s*(\d{1,2})일"
    match = re.match(pattern, text)
    if not match:
        return None

    period, day = match.groups()
    day = int(day)
    
    # 이번 달/다음 달에 따라 날짜 계산
    if period == "다음":
        months_to_add = 1
    else:  # 이번
        months_to_add = 0
        
    target_date = add_months(now, months_to_add)
    target_date = target_date.replace(day=min(day, 28))  # 일자 범위 체크
    
    return target_date.strftime("%Y-%m-%d") 