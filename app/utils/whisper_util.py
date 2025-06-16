import whisperx
import torch
from typing import Dict, List
from whisperx.diarize import DiarizationPipeline
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WhisperUtil:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        hf_token = os.getenv('HF_TOKEN')
        self.model = whisperx.load_model("base", self.device, compute_type="float32")
        self.diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=self.device)
    
    def transcribe(self, audio_path: str) -> Dict:
        
        result = self.model.transcribe(
            audio_path,
            batch_size=16,
            language='ko',
        )

        align_model, metadata = whisperx.load_align_model(language_code="ko", device=self.device)
        result = whisperx.align(result["segments"], align_model, metadata, audio_path, self.device)

        return result

    def diarize(self, audio_path: str) -> List[Dict]:
        """WhisperX로 화자 분리 수행"""
        diarize_segments = self.diarize_model(audio_path)
        return diarize_segments

    def integrate_segments(self, whisper_result: Dict, diarize_segments: List[Dict]) -> Dict:
        """Whisper 결과와 화자 분리 결과 통합
        
        Args:
            whisper_result: Whisper 변환 결과
            diarize_segments: 화자 분리 결과
            
        Returns:
            통합된 세그먼트 목록
        """
        integrated_result = whisperx.assign_word_speakers(diarize_segments, whisper_result)
        return {
            "segments": integrated_result["segments"]
        }

    def remove_words_from_segments(self, segments: List[Dict]) -> List[Dict]:
        """세그먼트에서 words 필드 제거
        
        Args:
            segments: 세그먼트 목록
            
        Returns:
            words 필드가 제거된 세그먼트 목록
        """
        cleaned_segments = []
        for segment in segments:
            cleaned_segment = {
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'],
                'speaker': segment['speaker']
            }
            cleaned_segments.append(cleaned_segment)
        return cleaned_segments