import whisperx
import torch
import re
from typing import Dict, List, Optional

class WhisperService:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = whisperx.load_model("small", self.device, compute_type="float32")
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        오디오 파일을 텍스트로 변환합니다.
        
        Args:
            audio_path (str): 오디오 파일 경로
            
        Returns:
            Dict: 변환된 텍스트와 세그먼트 정보를 포함한 딕셔너리
        """
        print("\n=== WhisperX 원본 결과 ===")
        result = self.model.transcribe(audio_path)
        print(result)
        print("========================\n")
        
        if "segments" in result:
            segments = result["segments"]
            # 각 세그먼트의 시간 정보를 소수점 2자리까지 반올림
            for segment in segments:
                segment["start"] = round(segment["start"], 2)
                segment["end"] = round(segment["end"], 2)
            
            return {
                "text": " ".join([s["text"] for s in segments]),
                "segments": segments
            }
        else:
            text = result.get("text", "")
            return {
                "text": text,
                "segments": []
            }

    def _process_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        세그먼트를 문장 단위로 처리합니다.
        
        Args:
            segments (List[Dict]): 원본 세그먼트 리스트
            
        Returns:
            List[Dict]: 처리된 문장 리스트
        """
        sentences_with_time = []
        current_text = ""
        start_time = None
        end_time = None
        
        for segment in segments:
            if not current_text:  # 새로운 문장 시작
                start_time = segment['start']
            
            current_text += segment['text']
            
            # 문장 종료 조건 확인 (마침표, 느낌표, 물음표)
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
        
        # 마지막 문장 처리
        if current_text:
            sentences_with_time.append({
                "text": current_text.strip(),
                "start_time": round(start_time, 2),
                "end_time": round(segments[-1]['end'], 2)
            })
            
        return sentences_with_time

    def transcribe(self, audio_path):
        try:
            result = self.model.transcribe(audio_path)
            return result["text"]
        finally:
            # 임시 파일 삭제
            if os.path.exists(audio_path):
                os.remove(audio_path) 