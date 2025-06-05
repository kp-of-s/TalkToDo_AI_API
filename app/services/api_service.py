import whisperx
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.date_util import DateUtil
from app.utils.bedrock_util import BedrockUtil

# Load environment variables
load_dotenv()

class APIService:
    def __init__(self):
        self.whisper_util = WhisperUtil()
        self.date_util = DateUtil()
        self.langchain_util = LangChainUtil()
        self.bedrock_util = BedrockUtil()

    def process_audio(self, audio_path: str, meeting_date: Optional[str] = None) -> Dict:
        try:
            # 음성→텍스트 변환
            result = self.whisper_util.speech_to_text(audio_path)
            print(result)
            
            # 화자 분리 수행
            diarize_segments = self.whisper_util.diarize(audio_path)
            print(diarize_segments)

            # 결과 결합
            result = whisperx.assign_word_speakers(diarize_segments, result)
            print(result)
            
            segments = result["segments"]
            for segment in segments:
                segment["start"] = round(segment["start"])
                segment["end"] = round(segment["end"])
            
            transcript = {
                "text": " ".join([s["text"] for s in segments]),
                "segments": segments
            }

            formatted_transcript = self._format_transcript(transcript)
            
            
            # 회의 요약
            summary = self.bedrock_util.summarize_meeting(formatted_transcript)
            print(summary)
            # 일정 추출
            schedule = self.bedrock_util.extract_schedule(formatted_transcript, meeting_date)
            print(schedule)
            # schedule 날짜 포메팅
            schedule = self.date_util.process_schedule_dates(schedule)

            # 할 일 추출
            todos = self.bedrock_util.extract_todos(formatted_transcript, meeting_date)
            print(todos)
            # todos 날짜 포메팅
            todos = self.date_util.process_todo_dates(todos)
            
            return {
                "meetingTranscript": transcript["segments"],
                "meetingSummary": summary,
                "todo": todos,
                "schedule": schedule
            }
            
        except Exception as e:
            print(f"음성 처리 중 오류 발생: {str(e)}")
            raise

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