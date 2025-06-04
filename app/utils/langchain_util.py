from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  # GPT 사용
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()

class LangChainUtil:
    RELATIVE_DATE_TEMPLATE = "남은 기간 (가능한 경우 'YYYY-MM-DDTHH:mm:ss' 형식으로, 불가능한 경우 '3일 후', '1주일 후', '2개월 후' 등으로 표기)"
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.output_parser = StrOutputParser()

    def create_chain(self, template: str):
        prompt = ChatPromptTemplate.from_template(template)
        return prompt | self.llm | self.output_parser

    def _format_transcript(self, transcript: Dict) -> str:
        """Whisper 결과를
        SPEAKER_1: ㅎㅇ
        SPEAKER_2: ㅇㅎ
        형식으로 변환."""
        formatted_text = []
        for segment in transcript["segments"]:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"]
            formatted_text.append(f"{speaker}: {text}")
        return "\n".join(formatted_text)

    def summarize_meeting(self, transcript: Dict) -> Dict:
        try:
            formatted_transcript = self._format_transcript(transcript)
            
            template = """
            너는 회의록 요약 전문가다.
            다음 회의록을 읽고, JSON 형식으로 요약하라.

            반드시 아래와 같은 JSON 형식으로 응답:
            {{
                "subject": "회의 주제",
                "summary": "회의 내용 요약"
            }}

            네가 요약할 회의록:
            {transcript}
            각 발언은 "화자: 내용" 형식임.
            """
            chain = self.create_chain(template)
            
            result = chain.invoke({"transcript": formatted_transcript})
            
            parsed_result = json.loads(result)
            
            return parsed_result
        except Exception as e:
            print(f"\n=== 에러 발생 ===")
            print(f"에러 타입: {type(e)}")
            print(f"에러 내용: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            raise

    def extract_schedule(self, transcript: Dict, meeting_date: Optional[str] = None) -> List[Dict]:
        """회의에서 논의된 일정을 추출합니다."""
        formatted_transcript = self._format_transcript(transcript)
        
        # 회의 날짜가 없으면 현재 날짜 사용
        if not meeting_date:
            meeting_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        template = f"""
        너는 일정을 추출하는 전문가다.
        다음 회의 내용에서 일정을 추출하라.
        현재 회의 날짜는 {{meeting_date}}이다.

        반드시 아래와 같은 JSON 형식으로 응답:
        [
            {{{{
                "text": "일정 내용",
                "start": 일정 시작까지 {self.RELATIVE_DATE_TEMPLATE},
                "end": 일정 종료까지 {self.RELATIVE_DATE_TEMPLATE},
                "place": 장소.
            }}}},
            ...
        ]
        단, start, end, place에 대한 내용이 없다면 없는 값에 null 입력

        네가 일정을 추출할 회의록:
        {{transcript}}
        각 발언은 "화자: 내용" 형식임.
        """
        chain = self.create_chain(template)
        result = chain.invoke({
            "transcript": formatted_transcript,
            "meeting_date": meeting_date
        })
        
        print("\n=== GPT 응답 ===")
        print(result)
        print("===============")
        
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"\n=== JSON 파싱 에러 ===")
            print(f"에러 위치: {e.pos}")
            print(f"에러 라인: {e.lineno}")
            print(f"에러 컬럼: {e.colno}")
            print(f"에러 내용: {str(e)}")
            return []

    def extract_todos(self, transcript: Dict, meeting_date: Optional[str] = None) -> List[Dict]:
        """회의에서 논의된 할 일을 추출합니다."""
        formatted_transcript = self._format_transcript(transcript)

        # 회의 날짜가 없으면 현재 날짜 사용
        if not meeting_date:
            meeting_date = datetime.now().strftime("%Y년 %m월 %d일")

        template = f"""
        너는 TODO 리스트를 추출하는 전문가다.
        다음 회의 내용에서 할 일(TODO)을 추출하라.
        현재 회의 날짜는 {{meeting_date}}이다.

        반드시 아래와 같은 JSON 형식으로 응답:
        [
            {{{{
                "text": "할 일 내용",
                "start": 할 일 시작까지 {self.RELATIVE_DATE_TEMPLATE},
                "end": 할 일 종료까지 {self.RELATIVE_DATE_TEMPLATE}
            }}}}, 
            ...
        ]
        단, start, end에 대한 내용이 없다면 없는 값에 null 입력

        네가 TODO를 추출할 회의록:
        {{transcript}}
        각 발언은 "화자: 내용" 형식임.
        """
        chain = self.create_chain(template)
        result = chain.invoke({
            "transcript": formatted_transcript,
            "meeting_date": meeting_date
        })
        
        print("\n=== GPT 응답 ===")
        print(result)
        print("===============")
        
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"\n=== JSON 파싱 에러 ===")
            print(f"에러 위치: {e.pos}")
            print(f"에러 라인: {e.lineno}")
            print(f"에러 컬럼: {e.colno}")
            print(f"에러 내용: {str(e)}")
            return [] 