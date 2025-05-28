import whisperx
import torch
from typing import Dict, List
from whisperx.diarize import DiarizationPipeline
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class WhisperUtil:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = whisperx.load_model("base", self.device, compute_type="float32")
        hf_token = os.getenv('HF_TOKEN')
        self.diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=self.device)
    
    def speech_to_text(self, audio_path: str) -> Dict:
        """WhisperX로 음성→텍스트 수행"""
        result = self.model.transcribe(audio_path, batch_size=16)
        return result

    def diarize(self, audio_path: str) -> List[Dict]:
        """WhisperX로 화자 분리 수행"""
        diarize_segments = self.diarize_model(audio_path)
        return diarize_segments

    def _process_segments(self, segments: List[Dict]) -> List[Dict]:
        sentences_with_time = []
        current_text = ""
        start_time = None
        end_time = None
        for segment in segments:
            if not current_text:
                start_time = segment['start']
            current_text += segment['text']
            if re.search(r'[.!?]$', segment['text']):
                end_time = segment['end']
                sentences_with_time.append({
                    "text": current_text.strip(),
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2)
                })
                current_text = ""
                start_time = None
                end_time = None
        if current_text:
            sentences_with_time.append({
                "text": current_text.strip(),
                "start_time": round(start_time, 2),
                "end_time": round(segments[-1]['end'], 2)
            })
        return sentences_with_time