import whisperx
import torch
from typing import Dict, List
from whisperx.diarize import DiarizationPipeline
import os
from dotenv import load_dotenv
"# from faster_whisper.transcribe import TranscriptionOptions"

# Load environment variables
load_dotenv()

class WhisperUtil:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        hf_token = os.getenv('HF_TOKEN')
        self.model = whisperx.load_model("base", self.device, compute_type="float32")
        self.diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=self.device)
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        # transcription_options = TranscriptionOptions(
        #     word_timestamps=True,
        #     no_speech_threshold=0.3,
        #     condition_on_previous_text=False,
        #     suppress_blank=True,
        #     max_new_tokens=50,
        #     clip_timestamps=30,
        #     hallucination_silence_threshold=0.5
        # )
        """

        result = self.model.transcribe(
            audio_path,
            batch_size=16
            # language='ko',
            # transcription_options=transcription_options,
        )
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