from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  # GPT 사용
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv
from app.templates.schedule import SCHEDULE_TEMPLATE
from app.templates.todo import TODO_TEMPLATE
from app.templates.meeting import SUMMARIZE_MEETING_TEMPLATE

# .env 파일 로드
load_dotenv()

class LangChainUtil:
    RELATIVE_DATE_TEMPLATE = "남은 기간 (가능한 경우 'YYYY-MM-DDTHH:mm:ss' 형식으로, 불가능한 경우 '3일 후', '1주일 후', '2개월 후' 등으로 표기)"
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.output_parser = StrOutputParser()

    def _remove_markdown_code_block(self, text: str) -> str:
        #마크다운 코드 블록을 제거합니다.
        text = text.strip()
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
        return text.strip()

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
            speaker = segment["speaker"]
            text = segment["text"]
            formatted_text.append(f"{speaker}: {text}")
        return formatted_text

    def create_contextual_chunks(self, segments: List[Dict]) -> List[Dict]:
        """회의 세그먼트를 문맥 기반으로 청크로 분리
        
        Args:
            segments: 회의 세그먼트 목록
            
        Returns:
            문맥 기반 청크 목록
        """
        try:
            # 세그먼트를 텍스트로 변환
            formatted_segments = []
            for segment in segments:
                speaker = segment.get("speaker", "Unknown")
                text = segment["text"]
                formatted_segments.append({
                    "text": f"{speaker}: {text}",
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "speaker": speaker,
                    "original_text": text
                })
            
            template = """
            너는 회의 대화의 문맥을 분석하는 전문가다.
            다음 대화 내용을 문맥 단위로 나누어라.
            
            대화 내용:
            {transcript}
            
            다음 기준으로 문맥을 나누어라:
            1. 주제의 연속성
            2. 논의 흐름의 자연스러움
            3. 문맥의 일관성
            4. 대화의 응집성
            
            반드시 아래와 같은 JSON 형식으로 응답:
            {{[
                {{
                    "chunk_id": "청크 ID",
                    "start_index": 시작 세그먼트 인덱스,
                    "end_index": 종료 세그먼트 인덱스,
                    "reason": "이 청크로 나눈 이유"
                }},
                ...
            ]}}
            """
            
            chain = self.create_chain(template)
            result = chain.invoke({
                "transcript": "\n".join(seg["text"] for seg in formatted_segments)
            })
            
            chunk_info = json.loads(result)
            
            chunks = []
            for chunk in chunk_info:
                start_idx = chunk["start_index"]
                end_idx = chunk["end_index"]
                
                chunk_segments = formatted_segments[start_idx:end_idx + 1]
                chunks.append({
                    "text": " ".join(seg["original_text"] for seg in chunk_segments),
                    "speakers": list(set(seg["speaker"] for seg in chunk_segments)),
                    "start_time": chunk_segments[0]["start"],
                    "end_time": chunk_segments[-1]["end"],
                    "segments": chunk_segments,
                    "metadata": {
                        "chunk_id": chunk["chunk_id"],
                        "reason": chunk["reason"],
                        "segment_count": len(chunk_segments)
                    }
                })
            
            return chunks
            
        except Exception as e:
            print(f"청크 생성 실패: {str(e)}")
            return [{
                "text": " ".join(seg["text"] for seg in segments),
                "speakers": list(set(seg.get("speaker", "Unknown") for seg in segments)),
                "start_time": segments[0].get("start", 0),
                "end_time": segments[-1].get("end", 0),
                "segments": segments,
                "metadata": {
                    "chunk_id": "fallback_chunk",
                    "reason": "청크 생성 실패로 인한 폴백",
                    "segment_count": len(segments)
                }
            }]

    def summarize_meeting(self, transcript: Dict) -> Dict:
        try:
            formatted_transcript = self._format_transcript(transcript)
            
            chain = self.create_chain(SUMMARIZE_MEETING_TEMPLATE)
            
            result = chain.invoke({"transcript": formatted_transcript})

            if result.strip().startswith("```"):
                result = self._remove_markdown_code_block(result)
            parsed_result = json.loads(result)

            print("\n=== 요약 ===")
            print(parsed_result)

            return parsed_result
       
                
        except Exception as e:
            print(f"\n=== 에러 발생 ===")
            print(f"에러 타입: {type(e)}")
            print(f"에러 내용: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            return {
                "subject": "회의 요약 실패",
                "summary": "회의 내용을 요약하는데 실패했습니다."
            }

    def extract_schedule(self, transcript: Dict, meeting_date: str) -> List[Dict]:
        """회의에서 논의된 일정을 추출합니다."""
        try:
            formatted_transcript = self._format_transcript(transcript)
            
            chain = self.create_chain(SCHEDULE_TEMPLATE)
            result = chain.invoke({
                "transcript": formatted_transcript,
                "meeting_date": meeting_date,
                "relative_date_template": self.RELATIVE_DATE_TEMPLATE
            })

            print("\n=== 일정 응답 ===")
            print(result)
            
            if result.strip().startswith("```"):
                result = self._remove_markdown_code_block(result)
            parsed_result = json.loads(result)

            print("\n=== 일정 ===")
            print(parsed_result)
            
            return parsed_result
                
        except Exception as e:
            print(f"\n=== 에러 발생 ===")
            print(f"에러 타입: {type(e)}")
            print(f"에러 내용: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            return []

    def extract_todos(self, transcript: Dict, meeting_date: str) -> List[Dict]:
        """회의에서 논의된 할 일을 추출합니다."""
        try:
            formatted_transcript = self._format_transcript(transcript)

            chain = self.create_chain(TODO_TEMPLATE)
            result = chain.invoke({
                "transcript": formatted_transcript,
                "meeting_date": meeting_date,
                "relative_date_template": self.RELATIVE_DATE_TEMPLATE
            })
            
            if result.strip().startswith("```"):
                result = self._remove_markdown_code_block(result)
            parsed_result = json.loads(result)

            print("\n=== 투두 ===")
            print(parsed_result)
            
            return parsed_result
                
        except Exception as e:
            print(f"\n=== 에러 발생 ===")
            print(f"에러 타입: {type(e)}")
            print(f"에러 내용: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            return [] 