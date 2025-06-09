import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.utils.s3_util import S3Util
from dotenv import load_dotenv

def test_s3_save():
    # 환경 변수 로드
    load_dotenv()
    
    # S3Util 인스턴스 생성
    s3_util = S3Util()
    
    # 테스트용 세그먼트 데이터
    test_segments = [
        {
            "speaker": "Speaker 1",
            "text": "안녕하세요, 테스트입니다.",
            "start": "00:00:00",
            "end": "00:00:05"
        },
        {
            "speaker": "Speaker 2",
            "text": "네, S3 저장 테스트를 진행하고 있습니다.",
            "start": "00:00:06",
            "end": "00:00:12"
        }
    ]
    
    # 테스트용 사용자 ID와 날짜
    test_user_id = "test_user"
    test_date = "2024-03-20"
    
    try:
        # S3에 저장 시도
        result = s3_util.save_meeting_segments(
            segments=test_segments,
            user_id=test_user_id,
            meeting_date=test_date
        )
        
        if result:
            print("✅ S3 저장 테스트 성공!")
            print(f"저장된 경로: {s3_util.prefix}{test_user_id}/{test_date}/meeting.txt")
        else:
            print("❌ S3 저장 테스트 실패")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_s3_save() 