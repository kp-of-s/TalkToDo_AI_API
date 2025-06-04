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
    'day': 'days',
    'week': 'weeks',
    'month': 'months',
    'year': 'years'
}

def handle_number_unit_pattern(text: str, base_date: datetime) -> Optional[str]:
    number_pattern = r"(\d+)(일|주|달|월|년)(\s*(후|뒤|전|앞))?"
    match = re.match(number_pattern, text)
    if not match:
        return None
    number, unit, _, direction = match.groups()
    number = int(number)
    if direction in ["전", "앞"]:
        number = -number
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