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
    try:
        # 1. STT - 화자 분리
        print("\n=== STT 및 화자 분리 결과 ===")
        transcript = api_service.process_audio(temp_path)
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