import whisperx
from typing import Dict, List
import os
from dotenv import load_dotenv
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.date_util import DateUtil

# Load environment variables
load_dotenv()

class APIService:
    def __init__(self):
        self.whisper_util = WhisperUtil()
        self.date_util = DateUtil()

    def process_audio(self, audio_path: str) -> Dict:
        try:
            # 음성→텍스트 변환
            result = self.whisper_util.speech_to_text(audio_path)
            
            # 화자 분리 수행
            diarize_segments = self.whisper_util.diarize(audio_path)
            
            # 결과 결합
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # 세그먼트 시간 정보 반올림
            if "segments" in result:
                segments = result["segments"]
                for segment in segments:
                    segment["start"] = round(segment["start"], 2)
                    segment["end"] = round(segment["end"], 2)
                
                transcript = {
                    "text": " ".join([s["text"] for s in segments]),
                    "segments": segments
                }
            else:
                text = result.get("text", "")
                transcript = {
                    "text": text,
                    "segments": []
                }

            # LangChain을 사용한 추가 처리
            langchain_util = LangChainUtil()
            
            # 회의 요약
            summary = langchain_util.summarize_meeting(transcript)
            
            # 일정 추출
            schedule = langchain_util.extract_schedule(transcript)
            # schedule 날짜 포메팅
            schedule = self.date_util.process_schedule_dates(schedule)

            # 할 일 추출
            todos = langchain_util.extract_todos(transcript)
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