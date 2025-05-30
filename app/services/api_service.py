import whisperx
from typing import Dict
import os
from dotenv import load_dotenv
from app.utils.whisper_util import WhisperUtil

# Load environment variables
load_dotenv()

class APIService:
    def __init__(self):
        self.whisper_util = WhisperUtil()

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
                
                return {
                    "text": " ".join([s["text"] for s in segments]),
                    "segments": segments
                }
            else:
                text = result.get("text", "")
                return {
                    "text": text,
                    "segments": []
                }
        except Exception as e:
            print(f"음성 처리 중 오류 발생: {str(e)}")
            raise 