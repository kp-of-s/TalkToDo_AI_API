"""
템플릿 모듈 패키지
"""

from .prompts import RELATIVE_DATE_TEMPLATE
from .meeting import SUMMARIZE_MEETING_TEMPLATE
from .schedule import SCHEDULE_TEMPLATE
from .todo import TODO_TEMPLATE

__all__ = [
    'RELATIVE_DATE_TEMPLATE',
    'SUMMARIZE_MEETING_TEMPLATE',
    'SCHEDULE_TEMPLATE',
    'TODO_TEMPLATE'
] 