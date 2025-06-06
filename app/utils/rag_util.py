from typing import List, Dict, Optional
import json
from datetime import datetime
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class RAGUtil:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket = os.getenv("S3_BUCKET")
        
        # S3 경로 설정
        self.raw_path = "meetings"
        self.processed_path = "processed"
        
    def _get_user_path(self, user_id: str, date: str) -> str:
        """사용자별 경로 생성"""
        year_month = date[:7]  # YYYY-MM
        return f"{self.raw_path}/{year_month}/user_{user_id}"
        
    def _get_processed_path(self, user_id: str, date: str) -> str:
        """처리된 데이터 경로 생성"""
        year_month = date[:7]  # YYYY-MM
        return f"{self.processed_path}/{year_month}/user_{user_id}"
        
    def save_meeting_segments(self, 
                            segments: List[Dict], 
                            user_id: str, 
                            meeting_date: str,
                            meeting_title: str) -> str:
        """회의 세그먼트 저장
        
        Args:
            segments: Whisper-화자분리 통합 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            meeting_title: 회의 제목
            
        Returns:
            저장된 파일의 S3 경로
        """
        # 파일명 생성
        filename = f"{meeting_date}_{meeting_title}.json"
        path = f"{self._get_user_path(user_id, meeting_date)}/{filename}"
        
        # 세그먼트 데이터 저장
        self.s3.put_object(
            Bucket=self.bucket,
            Key=path,
            Body=json.dumps({
                "segments": segments,
                "metadata": {
                    "user_id": user_id,
                    "meeting_date": meeting_date,
                    "meeting_title": meeting_title,
                    "created_at": datetime.now().isoformat()
                }
            }, ensure_ascii=False).encode('utf-8')
        )
        
        return path
        
    def get_meeting_segments(self, 
                           user_id: str, 
                           meeting_date: str,
                           meeting_title: str) -> Optional[Dict]:
        """회의 세그먼트 조회
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            meeting_title: 회의 제목
            
        Returns:
            세그먼트 데이터 또는 None
        """
        filename = f"{meeting_date}_{meeting_title}.json"
        path = f"{self._get_user_path(user_id, meeting_date)}/{filename}"
        
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=path)
            return json.loads(response['Body'].read().decode('utf-8'))
        except:
            return None
            
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
        prefix = f"{self.raw_path}/{year_month}/user_{user_id}/"
        
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            meetings = []
            for obj in response.get('Contents', []):
                if not obj['Key'].endswith('.json'):
                    continue
                    
                # 파일명에서 날짜와 제목 추출
                filename = obj['Key'].split('/')[-1]
                date, title = filename.replace('.json', '').split('_', 1)
                
                meetings.append({
                    "date": date,
                    "title": title,
                    "path": obj['Key'],
                    "last_modified": obj['LastModified'].isoformat()
                })
                
            return meetings
        except:
            return []
            
    def search_meetings(self, 
                       query: str, 
                       user_id: str,
                       year_month: Optional[str] = None) -> List[Dict]:
        """회의 내용 검색
        
        Args:
            query: 검색어
            user_id: 사용자 ID
            year_month: 검색할 년월 (YYYY-MM), None이면 전체 기간
            
        Returns:
            검색 결과 목록
        """
        # TODO: 벡터 검색 구현
        # 1. 쿼리 임베딩 생성
        # 2. 벡터 DB에서 유사한 세그먼트 검색
        # 3. 검색 결과 반환
        pass
        
    def get_meeting_context(self, 
                           user_id: str,
                           meeting_date: str,
                           meeting_title: str,
                           start_time: Optional[float] = None,
                           end_time: Optional[float] = None) -> List[Dict]:
        """특정 시간대의 회의 컨텍스트 조회
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜
            meeting_title: 회의 제목
            start_time: 시작 시간 (초)
            end_time: 종료 시간 (초)
            
        Returns:
            해당 시간대의 세그먼트 목록
        """
        data = self.get_meeting_segments(user_id, meeting_date, meeting_title)
        if not data:
            return []
            
        segments = data['segments']
        
        if start_time is not None and end_time is not None:
            return [
                s for s in segments 
                if start_time <= s['start'] <= end_time
            ]
        elif start_time is not None:
            return [
                s for s in segments 
                if s['start'] >= start_time
            ]
        elif end_time is not None:
            return [
                s for s in segments 
                if s['end'] <= end_time
            ]
            
        return segments 