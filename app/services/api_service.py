from typing import Dict, List, Optional
import os
from datetime import datetime
from app.utils.whisper_util import WhisperUtil
from app.services.rag_service import RAGService
from app.utils.audio_utils import save_audio_file, cleanup_temp_file

class APIService:
    def __init__(self, 
                 whisper_util: WhisperUtil,
                 rag_service: RAGService):
        self.whisper_util = whisper_util
        self.rag_service = rag_service
        
    def process_audio(self, 
                     audio_file,
                     user_id: str,
                     meeting_date: str) -> Dict:
        """오디오 파일 처리 및 저장
        
        Args:
            audio_file: 오디오 파일 객체
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            처리 결과 (요약, 할일, 일정)
        """
        # 임시 파일로 저장
        temp_path, error_response, status_code = save_audio_file(audio_file)
        if error_response:
            raise Exception(error_response)
            
        try:
            # 1. SST 수행
            whisper_result = self.whisper_util.transcribe(temp_path)
            
            # 2. 화자 분리 수행
            diarize_segments = self.whisper_util.diarize(temp_path)
            
            # 3. 세그먼트 통합
            integrated_segments = self.whisper_util.integrate_segments(whisper_result, diarize_segments)
            
            print("회의록 전문:", integrated_segments)
            print("유저 ID:", user_id)
            print("회의 날짜:", meeting_date)

            # 4. RAG 처리
            result = self.rag_service.process_meeting(
                segments=integrated_segments,
                user_id=user_id,
                meeting_date=meeting_date
            )
            
            return result
            
        finally:
            # 임시 파일 정리
            cleanup_temp_file(temp_path)