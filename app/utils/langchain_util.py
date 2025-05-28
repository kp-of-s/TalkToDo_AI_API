from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI  # GPT 사용시 주석 해제
from langchain_huggingface import HuggingFaceEndpoint
from typing import Dict, List
import json
import os

class LangChainUtil:
    def __init__(self):
        # GPT 사용시 아래 주석 해제
        # self.llm = ChatOpenAI()
        print("llm 초기화 진입")
        self.llm = HuggingFaceEndpoint(
            repo_id="eenzeenee/t5-base-korean-summarization",
            task="summarization",
            temperature=0.7,
            huggingfacehub_api_token=os.getenv('HF_TOKEN'),
            max_new_tokens=128,           # 요약이므로 128 정도로 충분
            return_full_text=False
        )
        self.output_parser = StrOutputParser()

    def create_chain(self, template: str):
        print("체인 생성 진입")
        prompt = ChatPromptTemplate.from_template(template)
        print("체인 생성 완료")
        return prompt | self.llm | self.output_parser

    def _format_transcript(self, transcript: Dict) -> str:
        """Whisper 결과를
        SPEAKER_1: ㅎㅇ
        SPEAKER_2: ㅇㅎ
        형식으로 변환."""
        print("포멧 변환 진입")
        formatted_text = []
        for segment in transcript["segments"]:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"]
            formatted_text.append(f"{speaker}: {text}")
        print("포멧 변환 완료")
        return "\n".join(formatted_text)

    def summarize_meeting(self, transcript: Dict) -> Dict:
        """회의 내용을 요약합니다."""
        try:
            print("\n=== summarize_meeting 시작 ===")
            formatted_transcript = self._format_transcript(transcript)
            print(f"포맷된 텍스트: {formatted_transcript}")
            
            template = """
            너는 회의록 요약 전문가다.
            다음 회의록을 읽고, JSON 형식으로 요약하라.
            각 발언은 "화자: 내용" 형식임.

            아래와 같은 JSON 형식으로 응답:
            {{
                "subject": "회의 주제",
                "summary": "회의 내용 요약"
            }}

            네가 요약할 회의록:
            {transcript}
            """
            print("체인 생성 시작")
            chain = self.create_chain(template)
            print("체인 생성 완료")
            
            print("LLM 호출 시작")
            result = chain.invoke({"transcript": formatted_transcript})
            print(f"LLM 응답: {result}")
            
            print("JSON 파싱 시작")
            parsed_result = json.loads(result)
            print(f"파싱된 결과: {parsed_result}")
            
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
        각 발언은 "화자: 내용" 형식임.

        아래와 같은 JSON 형식으로 응답:
        [
            {{
                "text": "일정 내용",
                "start": 시작시간,
                "end": 종료시간
            }},
            ...
        ]

        네가 일정을 추출할 회의록:
        {transcript}
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
        각 발언은 "화자: 내용" 형식으로 되어있습니다.

        아래와 같은 JSON 형식으로 응답:
        [
            {{
                "text": "할 일 내용",
                "start": 시작시간,
                "end": 종료시간
            }}, 
            ...
        ]

        네가 TODO를 추출할 회의록:
        {transcript}
        """
        chain = self.create_chain(template)
        result = chain.invoke({"transcript": formatted_transcript})
        return json.loads(result) 