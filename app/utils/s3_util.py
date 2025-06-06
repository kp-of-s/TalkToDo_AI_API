from typing import List, Dict, Optional
import json
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class S3Util:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
    def _generate_meeting_title(self, user_id: str, meeting_date: str) -> str:
        """회의 타이틀 생성
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            생성된 회의 타이틀
        """
        timestamp = datetime.now().strftime("%H%M%S")
        return f"{user_id}_{meeting_date}_{timestamp}"
        
    def save_meeting_segments(self,
                            segments: List[Dict],
                            user_id: str,
                            meeting_date: str) -> str:
        """회의 세그먼트를 S3에 저장
        
        Args:
            segments: 회의 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            저장된 파일의 S3 경로
        """
        # 회의 타이틀 생성
        meeting_title = self._generate_meeting_title(user_id, meeting_date)
        
        # S3 키 생성
        s3_key = f"users/{user_id}/meetings/{meeting_date}/{meeting_title}.json"
        
        # 데이터 저장
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps({
                    "segments": segments,
                    "user_id": user_id,
                    "meeting_date": meeting_date,
                    "meeting_title": meeting_title,
                    "created_at": datetime.now().isoformat()
                }, ensure_ascii=False),
                ContentType='application/json'
            )
            return s3_key
        except ClientError as e:
            print(f"Error saving to S3: {e}")
            raise
            
    def get_meeting_segments(self,
                           user_id: str,
                           meeting_date: str,
                           meeting_title: str) -> Optional[Dict]:
        """회의 세그먼트를 S3에서 조회
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            meeting_title: 회의 제목
            
        Returns:
            회의 데이터 또는 None
        """
        s3_key = f"users/{user_id}/meetings/{meeting_date}/{meeting_title}.json"
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            print(f"Error getting from S3: {e}")
            raise
            
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
        prefix = f"users/{user_id}/meetings/{year_month}/"
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            meetings = []
            for obj in response.get('Contents', []):
                # 파일명에서 meeting_title 추출
                meeting_title = os.path.splitext(os.path.basename(obj['Key']))[0]
                
                # 메타데이터 조회
                metadata = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                
                meetings.append({
                    "title": meeting_title,
                    "date": year_month,
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
                
            return meetings
        except ClientError as e:
            print(f"Error listing from S3: {e}")
            raise 