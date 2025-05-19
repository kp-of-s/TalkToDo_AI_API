from flask import Blueprint, request, jsonify
from app.services.whisper_service import WhisperService
from app.utils.audio_utils import save_audio_file

bp = Blueprint('transcribe', __name__)
whisper_service = WhisperService()

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    
    audio_file = request.files['audio']
    try:
        # 오디오 파일 저장
        audio_path = save_audio_file(audio_file)
        # WhisperX로 변환
        text = whisper_service.transcribe(audio_path)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 