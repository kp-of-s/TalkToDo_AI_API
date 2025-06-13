"""
회의 관련 템플릿 모듈
"""

SUMMARIZE_MEETING_TEMPLATE = """
너는 회의록 요약 전문가다.
다음 회의록을 읽고, JSON으로 요약하라.

반드시 아래와 같은 JSON으로 응답:
{{
    "subject": "회의 주제",
    "summary": "회의 내용 요약"
}}

네가 요약할 회의록:
{transcript}
각 발언은 "화자: 내용" 형식임.
""" 