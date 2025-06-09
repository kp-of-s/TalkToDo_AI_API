import os
import tempfile
from flask import request
from typing import Tuple, Optional

def save_audio_file(file) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """업로드된 오디오 파일을 임시 파일로 저장
    
    Args:
        file: 업로드된 파일 객체
        
    Returns:
        Tuple[임시 파일 경로, 에러 메시지, 상태 코드]
    """
    try:
        # 파일 확장자 검사
        if not file.filename.lower().endswith(('.mp3')):
            return None, "지원하지 않는 파일 형식입니다. MP3 파일만 지원합니다.", 400
            
        # 임시 파일 생성
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        temp_path = temp_file.name
        
        # 파일 저장
        file.save(temp_path)
        temp_file.close()
        
        return temp_path, None, None
        
    except Exception as e:
        return None, f"파일 저장 중 오류가 발생했습니다: {str(e)}", 500

def cleanup_temp_file(file_path: str) -> None:
    """임시 파일 삭제
    
    Args:
        file_path: 삭제할 파일 경로
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass  # 파일 삭제 실패는 무시

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