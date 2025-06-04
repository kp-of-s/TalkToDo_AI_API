import re
from datetime import datetime, timedelta
from typing import Optional
from .utils import add_months

PERIOD_MAP = {
    '일': 'days',
    '주': 'weeks',
    '달': 'months',
    '월': 'months',
    '년': 'years',
    '시간': 'hours',
    '분': 'minutes',
    '주일': 'weeks',
    '개월': 'months',
    '년간': 'years'
}

def handle_number_unit_pattern(text: str, base_date: datetime) -> Optional[str]:
    """상대적 기간 패턴 매칭 (3일 후, 2주 후, 5개월 후 등)"""
    number_pattern = r"(\d+)(일|주|주일|달|월|개월|년|년간|시간|분)(\s*(후|뒤))?"
    match = re.match(number_pattern, text)
    if not match:
        return None
        
    number, unit, _, _ = match.groups()
    number = int(number)
    unit = PERIOD_MAP.get(unit)
    if not unit:
        return None
        
    if unit == 'months':
        target_date = add_months(base_date, number)
    elif unit == 'years':
        target_date = base_date.replace(year=base_date.year + number)
    else:
        target_date = base_date + timedelta(**{unit: number})
        
    return target_date.strftime("%Y-%m-%d") 