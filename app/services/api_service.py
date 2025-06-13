from typing import Dict
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.audio_utils import save_audio_file, cleanup_temp_file
from app.utils.s3_util import S3Util
from app.utils.date_util import DateUtil
import json

class APIService:
    def __init__(self, 
                 whisper_util: WhisperUtil,
                 langchain_util: LangChainUtil,
                 s3_util: S3Util):
        self.whisper_util = whisper_util
        self.langchain_util = langchain_util
        self.s3_util = s3_util
        self.date_util = DateUtil()
        
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
            
            # words 필드 제거
            integrated_segments["segments"] = self.whisper_util.remove_words_from_segments(integrated_segments["segments"])
            
            # 4. 통합된 세그먼트를 S3에 저장
            self.s3_util.save_meeting_segments(integrated_segments["segments"], user_id, meeting_date)

            # 5. 추출
            summarize = self.langchain_util.summarize_meeting(integrated_segments)
            schedule = self.langchain_util.extract_schedule(integrated_segments, meeting_date)
            todos = self.langchain_util.extract_todos(integrated_segments, meeting_date)

            # 6. 날짜 처리
            processed_schedule = self.date_util.process_schedule_dates(schedule["items"])
            processed_todos = self.date_util.process_todo_dates(todos["items"])

            result = {
                "meetingTranscript": integrated_segments["segments"],
                "meetingSummary": summarize,
                "todos": processed_todos,
                "schedule": processed_schedule
            }

            print("resultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresult:", result)
            
            return result
            
        finally:
            # 임시 파일 정리
            cleanup_temp_file(temp_path)