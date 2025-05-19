import tempfile

def save_audio_file(audio_file):
    """오디오 파일을 임시 파일로 저장"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        audio_file.save(tmp.name)
        return tmp.name 