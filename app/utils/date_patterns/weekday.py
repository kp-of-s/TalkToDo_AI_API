import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

def handle_weekday_pattern(text: str, now: datetime) -> Optional[str]:
    """요일 패턴 매칭 (다음 주 금요일, 이번 주 목요일 등)"""
    pattern = r"(이번|다음|다다음|다다다음)\s*주(?:에\s+오는)?\s+(월|화|수|목|금|토|일)요일?"
    match = re.match(pattern, text)
    if not match:
        return None

    period, weekday = match.groups()
    weekday_map = {
        '월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6
    }
    target_weekday = weekday_map[weekday]

    # 현재 요일
    current_weekday = now.weekday()
    
    # 기간에 따른 주 계산
    if period == '이번':
        weeks = 0
    elif period == '다음':
        weeks = 1
    elif period == '다다음':
        weeks = 2
    elif period == '다다다음':
        weeks = 3
    else:
        return None

    # 목표 날짜 계산
    days_ahead = target_weekday - current_weekday
    if days_ahead <= 0:  # 목표 요일이 현재 요일보다 이전이면
        days_ahead += 7  # 다음 주로 이동
    
    target_date = now + timedelta(days=days_ahead + (weeks * 7))
    return target_date.strftime("%Y-%m-%d") 