import re
from datetime import datetime
from typing import Optional

def handle_year_month_day_pattern(text: str, now: datetime) -> Optional[str]:
    # 연/월/일 패턴 매칭
    pattern = r"(내년|올해)\s*(\d{1,2})월\s*(\d{1,2})일"
    match = re.match(pattern, text)
    if not match:
        return None

    period, month, day = match.groups()
    month, day = int(month), int(day)
    
    # 내년/올해에 따라 날짜 계산
    if period == "내년":
        year = now.year + 1
    else:  # 올해
        year = now.year
        
    try:
        target_date = now.replace(year=year, month=month, day=day)
        return target_date.strftime("%Y-%m-%d")
    except ValueError:
        return None 