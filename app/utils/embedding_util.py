from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class EmbeddingUtil:
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-ada-002"
        
    def get_embeddings(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환
        
        Args:
            text: 변환할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"임베딩 생성 실패: {str(e)}")
            return []
            
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 벡터로 변환
        
        Args:
            texts: 변환할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
            
        except Exception as e:
            print(f"배치 임베딩 생성 실패: {str(e)}")
            return []
            
    def process_segments(self, segments: List[Dict]) -> List[Dict]:
        """회의 세그먼트에 임베딩 추가
        
        Args:
            segments: 회의 세그먼트 목록
            
        Returns:
            임베딩이 추가된 세그먼트 목록
        """
        try:
            # 세그먼트 텍스트 추출
            texts = [segment["text"] for segment in segments]
            
            # 배치 임베딩 생성
            embeddings = self.get_embeddings_batch(texts)
            
            # 임베딩 추가
            for segment, embedding in zip(segments, embeddings):
                segment["embedding"] = embedding
                
            return segments
            
        except Exception as e:
            print(f"세그먼트 처리 실패: {str(e)}")
            return segments 