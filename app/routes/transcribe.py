from flask import Blueprint, request, jsonify
import tempfile
import os
from app.services.whisper_service import WhisperService

bp = Blueprint('transcribe', __name__)
whisper_service = WhisperService()

@bp.route('/')
def home():
    return jsonify({"message": "WhisperX 음성-텍스트 변환 API 서버입니다."})

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    audio_file = request.files['audio']
    
    # 파일 확장자 확인
    filename = audio_file.filename
    if not filename:
        return jsonify({"error": "파일 이름이 없습니다."}), 400
        
    # 지원하는 확장자 목록
    allowed_extensions = {'wav', 'mp3', 'm4a', 'ogg'}
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_extension not in allowed_extensions:
        return jsonify({"error": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp:
        audio_file.save(tmp.name)
        audio_path = tmp.name
    try:
        print("\n=== 음성 인식 시작 ===")
        result = whisper_service.transcribe_audio(audio_path)
        print("\n=== 최종 응답 데이터 ===")
        print(result)
        return jsonify(result)
    except Exception as e:
        print("\n=== 에러 발생 ===")
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(audio_path) 