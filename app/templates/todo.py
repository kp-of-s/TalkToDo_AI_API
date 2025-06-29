"""
할일 관련 템플릿 모듈
"""

TODO_TEMPLATE = """
너는 TODO 리스트를 추출하는 전문가다.
다음 회의 내용에서 할 일(TODO)을 추출하라.
현재 회의 날짜는 {meeting_date}이다.

반드시 아래와 같은 JSON 형식으로 응답:
{{
    "items": [
        {{
            "text": "할 일 내용",
            "start": 할 일 시작까지 {relative_date_template},
            "end": 할 일 종료까지 {relative_date_template}
        }}
    ]
}}
단, start, end에 대한 내용이 없다면 없는 값에 null 입력

네가 TODO를 추출할 회의록:
{transcript}
각 발언은 "화자: 내용" 형식임.
""" 