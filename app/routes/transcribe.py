from flask import Blueprint, request, jsonify
import tempfile
import os
from app.services.whisper_service import WhisperService

bp = Blueprint('transcribe', __name__)
whisper_service = WhisperService()

# 업로드 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    
    # 파일 확장자 추출
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'mp3'
    
    # 임시 파일 경로 생성
    temp_filename = f'temp_{os.urandom(8).hex()}.{file_extension}'
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    
    try:
        # 파일 저장
        audio_file.save(temp_path)
        print(f"\n=== 임시 파일 저장됨: {temp_path} ===")
        
        print("\n=== 음성 인식 시작 ===")
        result = whisper_service.transcribe_audio(temp_path)
        print("\n=== 최종 응답 데이터 ===")
        print(result)
        return jsonify(result)
    except Exception as e:
        print("\n=== 에러 발생 ===")
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"\n=== 임시 파일 삭제됨: {temp_path} ===")

@bp.route('/test_transcribe', methods=['POST'])
def test_transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    audio_file = request.files['audio']
    
    # 파일 확장자 확인
    filename = audio_file.filename
    if not filename:
        return jsonify({"error": "파일 이름이 없습니다."}), 400

    # 파일 확장자 추출
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'mp3'

    # 추가 텍스트 받기
    config = request.form.get('config', '')

    # 임시 파일 경로 생성
    temp_filename = f'temp_{os.urandom(8).hex()}.{file_extension}'
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)

    try:
        # 파일 저장
        audio_file.save(temp_path)
        print(f"\n=== 임시 파일 저장됨: {temp_path} ===")
        
        print("\n=== 음성 인식 시작 ===")
        result = whisper_service.transcribe_test(temp_path, config)
        print("\n=== 최종 응답 데이터 ===")
        print(result)
        return jsonify(result)
    except Exception as e:
        print("\n=== 에러 발생 ===")
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"\n=== 임시 파일 삭제됨: {temp_path} ===")