import whisperx
import torch
import os

class WhisperService:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = whisperx.load_model("large-v2", self.device)
    
    def transcribe(self, audio_path):
        try:
            result = self.model.transcribe(audio_path)
            return result["text"]
        finally:
            # 임시 파일 삭제
            if os.path.exists(audio_path):
                os.remove(audio_path) 