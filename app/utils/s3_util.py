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
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket = os.getenv("S3_BUCKET")
        self.prefix = os.getenv("S3_PREFIX", "meetings/")
        
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
        
    def save_meeting_segments(self, segments: List[Dict], user_id: str, meeting_date: str) -> bool:
        """회의 세그먼트를 S3에 텍스트 파일로 저장
        
        Args:
            segments: 회의 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            저장 성공 여부
        """
        try:
            # 파일 경로 생성
            file_key = f"{self.prefix}{user_id}/{meeting_date}/meeting.txt"
            
            # 텍스트 형식으로 변환
            text_content = []
            text_content.append(f"=== 회의 정보 ===")
            text_content.append(f"사용자: {user_id}")
            text_content.append(f"날짜: {meeting_date}")
            text_content.append(f"생성: {datetime.now().isoformat()}")
            text_content.append("")
            text_content.append("=== 회의 내용 ===")
            
            for segment in segments:
                speaker = segment.get('speaker', 'Unknown')
                text = segment.get('text', '').strip()
                if text:
                    text_content.append(f"{speaker}: {text}")
            
            # S3에 업로드
            self.s3.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body='\n'.join(text_content).encode('utf-8'),
                ContentType="text/plain"
            )
            
            print(f"세그먼트 저장 완료: {file_key}")
            return True
            
        except Exception as e:
            print(f"S3 저장 실패: {str(e)}")
            return False
            
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
            response = self.s3.get_object(
                Bucket=self.bucket,
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
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            meetings = []
            for obj in response.get('Contents', []):
                # 파일명에서 meeting_title 추출
                meeting_title = os.path.splitext(os.path.basename(obj['Key']))[0]
                
                # 메타데이터 조회
                metadata = self.s3.head_object(
                    Bucket=self.bucket,
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