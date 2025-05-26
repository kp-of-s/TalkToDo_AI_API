from flask import Blueprint, request, jsonify
import os
from app.services.whisper_service import WhisperService
from app.utils.audio_utils import save_audio_file, cleanup_temp_file

bp = Blueprint('api_router', __name__)
whisper_service = WhisperService()

# 업로드 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def home():
    return jsonify({"message": "작동댄다아아아아앗"})

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    
    audio_file = request.files['audio']
    temp_path, error_response, status_code = save_audio_file(audio_file, UPLOAD_FOLDER)
    
    if error_response:
        return error_response, status_code
    
    try:
        result = whisper_service.transcribe_audio(temp_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cleanup_temp_file(temp_path)