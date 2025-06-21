from typing import Dict
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.audio_utils import save_audio_file, cleanup_temp_file
from app.utils.s3_util import S3Util
from app.utils.date_util import DateUtil
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

class APIService:
    def __init__(self, 
                 whisper_util: WhisperUtil,
                 langchain_util: LangChainUtil,
                 s3_util: S3Util):
        self.whisper_util = whisper_util
        self.langchain_util = langchain_util
        self.s3_util = s3_util
        self.date_util = DateUtil()
        self.concurrent_processor = ConcurrentProcessor(langchain_util, self.date_util)
        
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

            # 5. 병렬로 추출 작업 수행
            results = self.concurrent_processor.process_all(integrated_segments, meeting_date)

            result = {
                "meetingTranscript": integrated_segments["segments"],
                "meetingSummary": results["summarize"],
                "todos": results["todos"],
                "schedule": results["schedule"]
            }

            print("resultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresult:", result)
            
            return result
            
        finally:
            # 임시 파일 정리
            cleanup_temp_file(temp_path)


class ConcurrentProcessor:
    """동시 실행을 위한 프로세서 클래스"""
    
    def __init__(self, langchain_util: LangChainUtil, date_util: DateUtil):
        self.langchain_util = langchain_util
        self.date_util = date_util
    
    def _validate_json_response(self, response, task_name: str) -> bool:
        """응답이 유효한 JSON인지 확인"""
        try:
            if isinstance(response, str):
                json.loads(response)
            elif isinstance(response, dict):
                # 딕셔너리는 이미 파싱된 JSON으로 간주
                pass
            else:
                print(f"{task_name}: 응답이 JSON 형식이 아닙니다")
                return False
            return True
        except json.JSONDecodeError:
            print(f"{task_name}: 유효하지 않은 JSON 형식입니다")
            return False
        except Exception as e:
            print(f"{task_name}: JSON 검증 중 오류: {str(e)}")
            return False
    
    def summarize_meeting(self, segments: Dict) -> Dict:
        """회의 요약 처리"""
        try:
            # 1. langchain_util.summarize_meeting 실행
            result = self.langchain_util.summarize_meeting(segments)
            
            # 2. JSON 검증
            if not self._validate_json_response(result, "회의 요약"):
                return {
                    "subject": "회의 요약 실패",
                    "summary": "회의 내용을 요약하는데 실패했습니다."
                }
            
            # 3. 결과 리턴
            return result
            
        except Exception as e:
            print(f"회의 요약 처리 실패: {str(e)}")
            return {
                "subject": "회의 요약 실패",
                "summary": "회의 내용을 요약하는데 실패했습니다."
            }
    
    def extract_schedule(self, segments: Dict, meeting_date: str) -> Dict:
        """일정 추출 처리"""
        try:
            # 1. langchain_util.extract_schedule 실행
            result = self.langchain_util.extract_schedule(segments, meeting_date)
            
            # 2. 날짜 처리
            if "items" in result:
                processed_items = self.date_util.process_schedule_dates(result["items"])
                result = {"items": processed_items}
            
            # 3. JSON 검증
            if not self._validate_json_response(result, "일정 추출"):
                return {"items": []}
            
            # 4. 결과 리턴
            return result
            
        except Exception as e:
            print(f"일정 추출 처리 실패: {str(e)}")
            return {"items": []}
    
    def extract_todos(self, segments: Dict, meeting_date: str) -> Dict:
        """할일 추출 처리"""
        try:
            # 1. langchain_util.extract_todos 실행
            result = self.langchain_util.extract_todos(segments, meeting_date)
            
            # 2. 날짜 처리
            if "items" in result:
                processed_items = self.date_util.process_todo_dates(result["items"])
                result = {"items": processed_items}
            
            # 3. JSON 검증
            if not self._validate_json_response(result, "할일 추출"):
                return {"items": []}
            
            # 4. 결과 리턴
            return result
            
        except Exception as e:
            print(f"할일 추출 처리 실패: {str(e)}")
            return {"items": []}
    
    def process_all(self, segments: Dict, meeting_date: str) -> Dict:
        """세 메소드를 동시에 실행"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_tasks():
                with ThreadPoolExecutor(max_workers=3) as executor:
                    # 세 태스크를 동시에 실행
                    tasks = [
                        loop.run_in_executor(executor, self.summarize_meeting, segments),
                        loop.run_in_executor(executor, self.extract_schedule, segments, meeting_date),
                        loop.run_in_executor(executor, self.extract_todos, segments, meeting_date)
                    ]
                    
                    # 모든 태스크 완료 대기
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 결과 처리
                    processed_results = {}
                    task_names = ["summarize", "schedule", "todos"]
                    
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            print(f"{task_names[i]} 태스크 실패: {str(result)}")
                            # 기본값 설정
                            if task_names[i] == "summarize":
                                processed_results[task_names[i]] = {
                                    "subject": "회의 요약 실패",
                                    "summary": "회의 내용을 요약하는데 실패했습니다."
                                }
                            else:
                                processed_results[task_names[i]] = {"items": []}
                        else:
                            processed_results[task_names[i]] = result
                    
                    return processed_results
            
            try:
                return loop.run_until_complete(run_tasks())
            finally:
                loop.close()
                
        except Exception as e:
            print(f"병렬 처리 실패: {str(e)}")
            # 실패 시 기본값 반환
            return {
                "summarize": {
                    "subject": "처리 실패",
                    "summary": "회의 처리에 실패했습니다."
                },
                "schedule": {"items": []},
                "todos": {"items": []}
            }