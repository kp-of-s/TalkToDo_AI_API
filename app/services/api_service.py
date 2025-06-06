from typing import Dict, List, Optional
import os
from datetime import datetime
from app.utils.whisper_util import WhisperUtil
from app.services.rag_service import RAGService

class APIService:
    def __init__(self, 
                 whisper_util: WhisperUtil,
                 rag_service: RAGService):
        self.whisper_util = whisper_util
        self.rag_service = rag_service
        
    def process_audio(self, 
                     audio_path: str,
                     user_id: str,
                     meeting_date: str) -> Dict:
        """오디오 파일 처리 및 저장
        
        Args:
            audio_path: 오디오 파일 경로
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            처리 결과 (요약, 할일, 일정)
        """
        # 1. SST 수행
        whisper_result = self.whisper_util.transcribe(audio_path)
        
        # 2. 화자 분리 수행
        diarize_segments = self.whisper_util.diarize(audio_path)
        
        # 3. 세그먼트 통합
        integrated_segments = self.whisper_util.integrate_segments(whisper_result, diarize_segments)
        
        # 4. RAG 처리
        result = self.rag_service.process_meeting(
            segments=integrated_segments,
            user_id=user_id,
            meeting_date=meeting_date
        )
        
        return result