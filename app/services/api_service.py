from typing import Dict
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.audio_utils import save_audio_file, cleanup_temp_file
import json

class APIService:
    def __init__(self, 
                 whisper_util: WhisperUtil,
                 langchain_util : LangChainUtil):
        self.whisper_util = whisper_util
        self.langchain_util = langchain_util
        
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
            # whisper_result = self.whisper_util.transcribe(temp_path)
            
            # 2. 화자 분리 수행
            # diarize_segments = self.whisper_util.diarize(temp_path)
            
            # 3. 세그먼트 통합
            # integrated_segments = self.whisper_util.integrate_segments(whisper_result, diarize_segments)
            integrated_segments = {
                "segments": [
                    {
                        "text": "다들 도착하셨나요? 그럼 회의 시작할게요. 먼저 디자인 팀 상황부터 공유해주시겠어요? 네, 디자인 팀은 이번 주까지 시안 1차 수정본 제출목별로 작업 중입니다. 주요 피드백 반영했고 마감은 목을까지 가능합니다. 좋아요. 개발팀은요? 기능 개발은 80% 열렸습니다. 어... 요그인 기능과 계시판 기능은 이번 주에 마무리할 예정이고 다음 주 월을 붙어 내부 테스트를 시작하려고 합니다.",
                        "start": 0.031,
                        "end": 28.162,
                        "speaker": "SPEAKER_00"
                    },
                    {
                        "text": "일정대로 잘 진행되고 있네요. 마케팅 쪽은 어떤가요? 마케팅 팀은 월초에 있을 프로모션을 준비 중입니다. 다만 이번 주 안으로 기획 초원을 작성하는 건 조금 타이트할 것 같은데 가능하다면 기획 초원 제출 기안을 다음 주 수요일까지로 도정해 주실 수 있을까요?",
                        "start": 28.583,
                        "end": 44.902,
                        "speaker": "SPEAKER_02"
                    },
                    {
                        "text": "음, 알겠어요. 전체 일정에는 영향이 크지 않으니 다음 주 수요일까지로 조정합시다. 그럼 지금 남은 과제는 기능 테스트 계획 수리, 디자인 수정 최종본 검토, 마케팅 기획 초원 전검 2-3가지로 정리할 수 있겠네요. 네, 테스트 계획 문서는 이번 주 금요일까지 작성해서 공유하겠습니다. 디자인 수정보는 목요일에 완성되는 대로 바로 공유 드리겠습니다.",
                        "start": 45.155,
                        "end": 68.965,
                        "speaker": "SPEAKER_01"
                    },
                    {
                        "text": "좋아요. 마지막으로 다음 회의 일정을 잡을게요. 4월 29일 월요일 오전 10시에 모두 괜찮으세요? 죄송한데 그날 오전에 내부 회의가 있어서 11시 이유로 밀어주실 수 있을까요? 저는 괜찮습니다. 저도 11시이면 문제 없습니다. 알겠습니다. 그럼 다음 회의는 4월 29일 월요일 오전 11시로 확정하겠습니다. 오늘 회의는 여기까지 하겠습니다. 모두 수고하셨습니다.",
                        "start": 69.134,
                        "end": 96.472,
                        "speaker": "SPEAKER_01"
                    }
                ]
            }
            
            print("회의록 전문:", integrated_segments)
            print("유저 ID:", user_id)
            print("회의 날짜:", meeting_date)

            # 4. 추출

            summarize = self.langchain_util.summarize_meeting(integrated_segments)
            schedule = self.langchain_util.extract_schedule(integrated_segments, meeting_date)
            todos = self.langchain_util.extract_todos(integrated_segments, meeting_date)


            result = {
                "meetingTranscript": integrated_segments,
                "meetingSummary": summarize,
                "todos": todos,
                "schedule": schedule
            }

            print("resultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresultresult:", result)
            
            return result
            
        finally:
            # 임시 파일 정리
            cleanup_temp_file(temp_path)