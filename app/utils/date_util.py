import dateparser
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from .date_patterns.number_unit import handle_number_unit_pattern

class DateUtil:
    @staticmethod
    def parse_date(date_str: str, settings: Optional[Dict[str, Any]] = None) -> Optional[datetime]:
        """날짜 문자열을 datetime 객체로 변환"""
        if not date_str:
            return None
            
        # Java LocalDateTime 형식 확인 (YYYY-MM-DDTHH:mm:ss)
        java_date_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
        if re.match(java_date_pattern, date_str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
            
        # 상대적 날짜 전처리 시도
        preprocessed_date = DateUtil.preprocess_relative_date(date_str)
        if preprocessed_date:
            # 시간 정보 추출
            time_info = None
            time_pattern = r"(오전|오후)?\s*(\d{1,2})시(?:\s*(\d{1,2})분)?"
            time_match = re.search(time_pattern, date_str)
            if time_match:
                am_pm, hour, minute = time_match.groups()
                hour = int(hour)
                if am_pm == "오후" and hour < 12:
                    hour += 12
                elif am_pm == "오전" and hour == 12:
                    hour = 0
                minute = int(minute) if minute else 0
                time_info = f"{hour:02d}:{minute:02d}:00"
            
            if time_info:
                try:
                    return datetime.strptime(f"{preprocessed_date} {time_info}", "%Y-%m-%d %H:%M:%S")
                except:
                    pass
            return datetime.strptime(preprocessed_date, "%Y-%m-%d")
            
        return None

    @staticmethod
    def format_for_java(date: datetime) -> str:
        """datetime을 Java 호환 형식의 문자열로 변환"""
        if not date:
            return None
        return date.strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def process_schedule_dates(schedule: List[Dict]) -> List[Dict]:
        """일정 데이터의 날짜 정보를 Java 호환 형식으로 변환"""
        processed_schedules = []
        for item in schedule:
            processed_item = {
                'text': item.get('text', ''),
                'place': item.get('place', ''),
                'start': None,
                'end': None
            }
            
            # 시작 시간 처리
            start_text = item.get('start', '')
            if start_text:
                start_date = DateUtil.parse_date(start_text)
                if start_date:
                    processed_item['start'] = DateUtil.format_for_java(start_date)
            
            # 종료 시간 처리
            end_text = item.get('end', '')
            if end_text:
                end_date = DateUtil.parse_date(end_text)
                if end_date:
                    processed_item['end'] = DateUtil.format_for_java(end_date)
            
            processed_schedules.append(processed_item)
            
        return processed_schedules

    @staticmethod
    def process_todo_dates(todos: List[Dict]) -> List[Dict]:
        """할 일 데이터의 날짜 정보를 Java 호환 형식으로 변환"""
        processed_todos = []
        for item in todos:
            processed_item = {
                'text': item.get('text', ''),
                'start': None,
                'end': None
            }
            
            # 시작 시간 처리
            start_text = item.get('start', '')
            if start_text:
                start_date = DateUtil.parse_date(start_text)
                if start_date:
                    processed_item['start'] = DateUtil.format_for_java(start_date)
            
            # 종료 시간 처리
            end_text = item.get('end', '')
            if end_text:
                end_date = DateUtil.parse_date(end_text)
                if end_date:
                    processed_item['end'] = DateUtil.format_for_java(end_date)
            
            processed_todos.append(processed_item)
            
        return processed_todos

    @staticmethod
    def preprocess_relative_date(text: str) -> Optional[str]:
        """상대적 날짜 표현을 실제 날짜 문자열로 변환"""
        if not text:
            return None
            
        now = datetime.now()
        return handle_number_unit_pattern(text, now)

if __name__ == "__main__":
    DateUtil.test_date_parsing()
