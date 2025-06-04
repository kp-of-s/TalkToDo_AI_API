import dateparser
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .date_patterns.weekday import handle_weekday_pattern
from .date_patterns.month_day import handle_month_day_pattern
from .date_patterns.year_month_day import handle_year_month_day_pattern
from .date_patterns.number_unit import handle_number_unit_pattern
from .date_patterns.number_unit import PERIOD_MAP
from .date_patterns.utils import add_months

class DateUtil:
    # 요일 매핑
    WEEKDAY_MAP = {
        '월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6,
    }
    
    # 기간 단위 매핑
    PERIOD_MAP = {
        '일': 'days',
        '주': 'weeks',
        '달': 'months',
        '월': 'months',
        '년': 'years',
    }

    @staticmethod
    def parse_date(date_str: str, settings: Optional[Dict[str, Any]] = None) -> Optional[datetime]:
        """날짜 문자열을 datetime 객체로 변환"""
        if not date_str:
            return None
            
        # 1. 상대적 날짜 전처리 시도
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
            
        # 2. dateparser로 직접 파싱 시도
        default_settings = {
            'DATE_ORDER': 'YMD',
            'RELATIVE_BASE': datetime.now(),
            'PREFER_DATES_FROM': 'future',
        }
        
        if settings:
            default_settings.update(settings)
            
        try:
            parsed_date = dateparser.parse(date_str, settings=default_settings, languages=['ko'])
            return parsed_date
        except Exception as e:
            print(f"날짜 파싱 중 오류 발생: {str(e)}")
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
                    
                    # 종료 시간이 없으면 시작 시간으로부터 1시간 후로 설정
                    if not item.get('end'):
                        end_date = start_date + timedelta(hours=1)
                        processed_item['end'] = DateUtil.format_for_java(end_date)
            
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
                    
                    # 종료 시간이 없으면 시작 시간으로부터 1시간 후로 설정
                    if not item.get('end'):
                        end_date = start_date + timedelta(hours=1)
                        processed_item['end'] = DateUtil.format_for_java(end_date)
            
            # 종료 시간 처리
            end_text = item.get('end', '')
            if end_text:
                end_date = DateUtil.parse_date(end_text)
                if end_date:
                    processed_item['end'] = DateUtil.format_for_java(end_date)
            
            processed_todos.append(processed_item)
            
        return processed_todos

    # 내부 사용 메소드들
    @staticmethod
    def preprocess_relative_date(text: str) -> Optional[str]:
        """상대적 날짜 표현을 실제 날짜 문자열로 변환"""
        if not text:
            return None
            
        now = datetime.now()
        
        # 각 패턴 처리 함수를 순차적으로 시도
        result = (
            handle_weekday_pattern(text, now) or
            handle_month_day_pattern(text, now) or
            handle_year_month_day_pattern(text, now) or
            handle_number_unit_pattern(text, now)
        )
        
        return result

    @staticmethod
    def _get_weekday_number(weekday: str) -> Optional[int]:
        """요일 문자열을 숫자로 변환 (월=0, 화=1, ...)"""
        return DateUtil.WEEKDAY_MAP.get(weekday.lower())

    @staticmethod
    def _add_months(date: datetime, months: int) -> datetime:
        """월 단위로 날짜 더하기"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date.replace(year=year, month=month, day=day)

    @staticmethod
    def test_date_parsing():
        """날짜 파싱 테스트"""
        test_cases = [
            # 요일 패턴
            "다음 주 금요일",
            "다음 주 금요일 오전 10시",
            "이번 주 목요일",
            
            # 월/일 패턴
            "다음 달 3일",
            "이번 달 15일",
            
            # 연/월/일 패턴
            "내년 5월 10일",
            "올해 12월 25일",
            
            # 숫자+단위 패턴
            "3일 뒤",
            "2주 후",
            "5개월 후",
            
            # 기타
            "내일",
            "내일 오후 2시",
            
            # 특이사항
            "다음주에 오는 금요일",
            "다음주에 오는 금요일 오전 10시",
            "이번주에 오는 목요일",
            "다다음주 월요일",
            "다다다음주 월요일 오전 10시"
        ]
        
        print("\n=== 날짜 파싱 테스트 ===")
        for test in test_cases:
            result = DateUtil.parse_date(test)
            print(f"입력: {test}")
            print(f"결과: {result}")
            if result:
                print(f"포맷팅: {DateUtil.format_for_java(result)}")
            print("---")

if __name__ == "__main__":
    DateUtil.test_date_parsing()
