from flask import Blueprint, request, jsonify
import os
from app.services.api_service import APIService
from app.utils.audio_utils import save_audio_file, cleanup_temp_file
from app.utils.langchain_util import LangChainUtil

bp = Blueprint('api_router', __name__)
api_service = APIService()
langchain_util = LangChainUtil()

# 업로드 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def home():
    return jsonify({"message": "작동댄다아아아아앗"})

@bp.route('/process-meeting', methods=['POST'])
def process_meeting():
    """음성 파일을 받아 STT, 화자 분리, 요약, 일정 추출, TODO 추출을 순차적으로 수행합니다."""
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    
    audio_file = request.files['audio']
    temp_path, error_response, status_code = save_audio_file(audio_file, UPLOAD_FOLDER)
    
    if error_response:
        return error_response, status_code
    print(f"HF_TOKEN: {os.getenv('HF_TOKEN')}")  # 토큰이 제대로 설정되어 있는지 확인
    try:
        # 1. STT - 화자 분리
        print("\n=== STT 및 화자 분리 결과 ===")
        # transcript = api_service.process_audio(temp_path)  # 기존 코드 주석 처리
        transcript = {
            "text": "다들 도착하셨나요? 그럼 회의 시작할게요. 먼저 디자인 팀 상황부터 공유해주시겠어요? 네, 디자인 팀은 이번 주까지 시안 1차 수정본 제출목별로 작업 중입니다. 주요 피드백 반 영향고 마감은 목을까지 가능합니다. 좋아요. 개발팀은요? 기능 개발은 80% 열렸습니다. 어... 요그인 기능과 계시판 기능은 이번 주에 마무리할 예정이고 다음 주 월을 붙어 내부 테스트를 시작 하려고 합니다.  일정대로 잘 진행되고 있네요. 마케팅 쪽은 어떤가요? 마케팅 팀은 월초에 있을 프로모션을 준비 중입니다. 다만 이번 주 안으로 기획 초원을 작성하는 건 조금 타이트할 것 같은데 가능하다면 기획 초원 제출 기안을 다음 주 수요일까지로 도정해 주실 수 있을까요?  음, 알겠어요. 전체 일정에는 영향이 크지 않으니 다음 주 수요일까지로 조정합시다. 그럼 지금 남은 과제는 기능 테스트 계획 수리, 디자인 수정 최종본 검토, 마케팅 기획 초원 전검 2-3가지로 정리할  수 있겠네요. 네, 테스트 계획 문서는 이번 주 금요일까지 작성해서 공유하겠습니다. 디자인 수정보는 목요일에 완성되는 대로 바로 공유 드리겠습니다.  좋아요. 마지막으로 다음 회의 일정을 잡을게요. 4월 29일 월요일 오전 10시에 모두 괜찮으세요? 죄송한데 그날 오전에 내부 회의가 있어 서 11시 이유로 밀어주실 수 있을까요? 저는 괜찮습니다. 저도 11시이면 문제 없습니다. 알겠습니다. 그럼 다음 회의는 4월 29일 월요일 오전 11시로 확정하겠습니다. 오늘 회의는 여기까지 하겠 습니다. 모두 수고하셨습니다.",
            "segments": [
                {
                    "speaker": "SPEAKER_00",
                    "text": "다들 도착하셨나요? 그럼 회의 시작할게요. 먼저 디자인 팀 상황부터 공유해주시 겠어요? 네, 디자인 팀은 이번 주까지 시안 1차 수정본 제출목별로 작업 중입니다. 주요 피드백 반영했고 마감은 목을까지 가능합니다. 좋아요. 개발팀은요? 기능 개발은 80% 열렸습니다. 어... 요그인 기능과 계시판 기능은 이번 주에 마무리할 예정이고 다음 주 월을 붙어 내부 테스트를 시작하려고 합니다.",
                    "start": 0.03,
                    "end": 28.16
                },
                {
                    "speaker": "SPEAKER_02",
                    "text": "일정대로 잘 진행되고 있네요. 마케팅 쪽은 어떤가요? 마케팅 팀은 월초에 있을 프로모션을 준비 중입니다. 다만 이번 주 안으로 기획 초원을 작성하는 건 조금 타이트할 것 같은데 가능하다면 기획 초원 제출 기안을 다음 주 수요일까지로 도정해 주실 수 있을까요?",
                    "start": 28.58,
                    "end": 44.90
                },
                {
                    "speaker": "SPEAKER_01",
                    "text": "음, 알겠어요. 전체 일정에는 영향이 크지 않으니 다음 주 수요일까지로 조정합시다. 그럼 지금 남은 과제는 기능 테스트 계획 수리, 디자인 수정 최종본 검토, 마케팅 기획 초원 전검 2-3가지로 정리할 수 있겠네요. 네, 테스트 계획 문서는 이번 주 금요일까지 작성해서 공유하겠습니다. 디자인 수정보는 목요일에 완성되는 대로 바로 공유 드리겠습니다.",
                    "start": 45.16,
                    "end": 68.97
                },
                {
                    "speaker": "SPEAKER_01",
                    "text": "좋아요. 마지막으로 다음 회의 일정을 잡을게요. 4월 29일 월요일 오전 10시에 모두 괜찮으세요? 죄송한데 그날 오전에 내부 회의가 있어서 11시 이유로 밀어주실 수 있을까요? 저는 괜찮습니다. 저도 11시이면 문제 없습니다. 알겠습니다. 그럼 다음 회의는 4월 29일 월요일 오전 11시로 확정하겠습니다. 오늘 회의는 여기까지 하겠습니다. 모두 수고하셨습니다.",
                    "start": 69.13,
                    "end": 96.47
                }
            ]
        }
        print(f"전체 텍스트: {transcript['text']}")
        print("세그먼트:")
        for segment in transcript["segments"]:
            print(f"- {segment['speaker']}: {segment['text']} ({segment['start']:.2f}s ~ {segment['end']:.2f}s)")
        
        # 2. 회의 내용 요약
        print("\n=== 회의 요약 ===")
        summary = langchain_util.summarize_meeting(transcript)
        print(f"주제: {summary['subject']}")
        print(f"요약: {summary['summary']}")
        
        # 3. 일정 추출
        print("\n=== 일정 추출 ===")
        schedule = langchain_util.extract_schedule(transcript)
        for s in schedule:
            print(f"- {s['text']} ({s['start']} ~ {s['end']})")
        
        # 4. 투두 추출
        print("\n=== TODO 추출 ===")
        todos = langchain_util.extract_todos(transcript)
        for todo in todos:
            print(f"- {todo['text']} ({todo['start']} ~ {todo['end']})")
        
        return jsonify({
            "meetingTranscript": transcript["segments"],
            "meetingSummary": summary,
            "todo": todos,
            "schedule": schedule
        })
    except Exception as e:
        print(f"\n=== 에러 발생 ===")
        print(f"에러 내용: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cleanup_temp_file(temp_path)