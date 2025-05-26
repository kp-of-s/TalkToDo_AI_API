import tempfile
import os
from flask import jsonify

def save_audio_file(audio_file, upload_folder: str) -> tuple:
    """오디오 파일을 저장하고 저장된 경로를 반환합니다."""
    filename, file_extension, error_response, status_code = validate_audio_file(audio_file)
    if error_response:
        return None, error_response, status_code
    
    # 임시 파일 경로 생성
    temp_filename = f'temp_{os.urandom(8).hex()}.{file_extension}'
    temp_path = os.path.join(upload_folder, temp_filename)
    
    try:
        # 파일 저장
        audio_file.save(temp_path)
        print(f"\n=== 임시 파일 저장됨: {temp_path} ===")
        return temp_path, None, None
    except Exception as e:
        return None, jsonify({"error": str(e)}), 500

def cleanup_temp_file(file_path: str) -> None:
    """임시 파일을 삭제합니다."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"\n=== 임시 파일 삭제됨: {file_path} ===")
        except Exception as e:
            print(f"\n=== 임시 파일 삭제 실패: {str(e)} ===")

def validate_audio_file(audio_file) -> tuple:
    """오디오 파일을 검증하고 파일명과 확장자를 반환합니다."""
    if not audio_file:
        return None, None, jsonify({"error": "audio 파일을 다시 보내십시오."}), 400
    
    filename = audio_file.filename
    if not filename:
        return None, None, jsonify({"error": "파일 이름이 누락되었습니다."}), 400
    
    file_extension = get_file_extension(filename)
    return filename, file_extension, None, None

def get_file_extension(filename: str) -> str:
    """파일 확장자를 추출합니다."""
    if not filename:
        return 'mp3'
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else 'mp3'

"""TODO: 오디오 파일 노이즈 제거 등등"""