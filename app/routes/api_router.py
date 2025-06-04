from flask import Blueprint, request, jsonify
import os
from app.services.api_service import APIService
from app.utils.audio_utils import save_audio_file, cleanup_temp_file

bp = Blueprint('api_router', __name__)
api_service = APIService()

# 업로드 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def home():
    return jsonify({"message": "작동댄다아아아아앗"})

@bp.route('/process-meeting', methods=['POST'])
def process_meeting():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    
    audio_file = request.files['audio']
    meeting_date = request.form.get('meeting_date')
    temp_path, error_response, status_code = save_audio_file(audio_file, UPLOAD_FOLDER)
    if error_response:
        return error_response, status_code
    
    try:
        result = api_service.process_audio(temp_path, meeting_date)
        
        print("\n=== 처리 결과 ===")
        print(f"전체 텍스트: {result['meetingTranscript']}")
        print(f"요약: {result['meetingSummary']}")
        print(f"일정: {result['schedule']}")
        print(f"할 일: {result['todo']}")
        print(result)
        
        return jsonify(result)
    except Exception as e:
        print(f"\n=== 에러 발생 ===")
        print(f"에러 내용: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cleanup_temp_file(temp_path)