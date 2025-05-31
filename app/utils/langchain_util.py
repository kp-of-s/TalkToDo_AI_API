from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  # GPT 사용
from typing import Dict, List
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class LangChainUtil:
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

            아래와 같은 JSON 형식으로 응답:
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

    def extract_schedule(self, transcript: Dict) -> List[Dict]:
        """회의에서 논의된 일정을 추출합니다."""
        formatted_transcript = self._format_transcript(transcript)
        template = """
        너는 일정을 추출하는 전문가다.
        다음 회의 내용에서 일정을 추출하라.

        아래와 같은 JSON 형식으로 응답:
        [
            {{
                "text": "일정 내용",
                "start": 일정 시작 일자,
                "end": 일정 종료 일자
            }},
            ...
        ]

        네가 일정을 추출할 회의록:
        {transcript}
        각 발언은 "화자: 내용" 형식임.
        """
        chain = self.create_chain(template)
        result = chain.invoke({"transcript": formatted_transcript})
        return json.loads(result)

    def extract_todos(self, transcript: Dict) -> List[Dict]:
        """회의에서 논의된 할 일을 추출합니다."""
        formatted_transcript = self._format_transcript(transcript)
        template = """
        너는 TODO 리스트를 추출하는 전문가다.
        다음 회의 내용에서 할 일(TODO)을 추출해주세요.

        아래와 같은 JSON 형식으로 응답:
        [
            {{
                "text": "할 일 내용",
                "start": 할 일 시작 일자,
                "end": 할 일 종료 일자
            }}, 
            ...
        ]

        네가 TODO를 추출할 회의록:
        {transcript}
        각 발언은 "화자: 내용" 형식임.
        """
        chain = self.create_chain(template)
        result = chain.invoke({"transcript": formatted_transcript})
        return json.loads(result) 