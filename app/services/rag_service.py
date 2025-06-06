from typing import List, Dict, Optional
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from app.utils.bedrock_util import BedrockUtil
from app.utils.s3_util import S3Util

load_dotenv()

class RAGService:
    def __init__(self, bedrock_util: BedrockUtil, s3_util: S3Util):
        self.bedrock_util = bedrock_util
        self.s3_util = s3_util
        
    def process_meeting(self, 
                       segments: List[Dict], 
                       user_id: str, 
                       meeting_date: str,
                       meeting_title: str) -> Dict:
        """회의 데이터 처리 및 저장
        
        Args:
            segments: Whisper-화자분리 통합 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            meeting_title: 회의 제목
            
        Returns:
            처리 결과 (저장 경로, 요약, 할일, 일정)
        """
        # 1. 세그먼트 저장
        path = self.s3_util.save_meeting_segments(
            segments=segments,
            user_id=user_id,
            meeting_date=meeting_date,
            meeting_title=meeting_title
        )
        
        # 2. 텍스트 추출 및 처리
        formatted_text = self._format_segments(segments)
        
        # 3. 요약/할일/일정 추출
        summary = self.bedrock_util.summarize_meeting(formatted_text)
        todos = self.bedrock_util.extract_todos(formatted_text, meeting_date)
        schedules = self.bedrock_util.extract_schedule(formatted_text, meeting_date)
        
        return {
            "path": path,
            "meetingTranscript": formatted_text,
            "meetingSummary": summary,
            "todo": todos,
            "schedule": schedules
        }
        
    def get_meeting_content(self, 
                          user_id: str, 
                          meeting_date: str,
                          meeting_title: str) -> Optional[Dict]:
        """회의 내용 조회 및 처리
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            meeting_title: 회의 제목
            
        Returns:
            처리된 회의 내용 또는 None
        """
        # 1. 세그먼트 조회
        data = self.s3_util.get_meeting_segments(
            user_id=user_id,
            meeting_date=meeting_date,
            meeting_title=meeting_title
        )
        
        if not data:
            return None
            
        # 2. 텍스트 추출 및 처리
        formatted_text = self._format_segments(data["segments"])
        
        # 3. 요약/할일/일정 추출
        summary = self.bedrock_util.summarize_meeting(formatted_text)
        todos = self.bedrock_util.extract_todos(formatted_text, meeting_date)
        schedules = self.bedrock_util.extract_schedule(formatted_text, meeting_date)
        
        return {
            "segments": data["segments"],
            "meetingTranscript": formatted_text,
            "meetingSummary": summary,
            "todo": todos,
            "schedule": schedules
        }
        
    def list_user_meetings(self, 
                          user_id: str, 
                          year_month: str) -> List[Dict]:
        """사용자의 회의 목록 조회
        
        Args:
            user_id: 사용자 ID
            year_month: 년월 (YYYY-MM)
            
        Returns:
            회의 메타데이터 목록
        """
        return self.s3_util.list_user_meetings(user_id, year_month)
        
    def _format_segments(self, segments: List[Dict]) -> str:
        """세그먼트를 텍스트 형식으로 변환
        
        Args:
            segments: 세그먼트 목록
            
        Returns:
            포맷된 텍스트
        """
        formatted_text = []
        for segment in segments:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"]
            formatted_text.append(f"{speaker}: {text}")
        return "\n".join(formatted_text) 