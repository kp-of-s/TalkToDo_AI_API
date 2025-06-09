from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from datetime import datetime

load_dotenv()

class VectorDBUtil:
    def __init__(self):
        """Pinecone 벡터 DB 초기화"""
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Pinecone 클라이언트 초기화
        self.pc = Pinecone(api_key=api_key)
        
            
        self.index = self.pc.Index(index_name)
        
    def store_vectors(self, 
                     vectors: List[Dict],
                     user_id: str,
                     meeting_date: str,
                     meeting_title: str) -> bool:
        """회의 세그먼트의 벡터를 저장
        
        Args:
            vectors: 벡터 데이터 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜
            meeting_title: 회의 제목
            
        Returns:
            저장 성공 여부
        """
        try:
            # 벡터 데이터 준비
            vector_data = []
            for i, vector in enumerate(vectors):
                vector_id = f"{user_id}_{meeting_date}_{meeting_title}_{i}"
                metadata = {
                    "user_id": user_id,
                    "meeting_date": meeting_date,
                    "meeting_title": meeting_title,
                    "segment_index": i,
                    "text": vector["text"],
                    "speaker": vector.get("speaker", "Unknown"),
                    "start": vector.get("start", 0),
                    "end": vector.get("end", 0),
                    "created_at": datetime.now().isoformat()
                }
                vector_data.append((vector_id, vector["embedding"], metadata))
            
            # 벡터 저장
            self.index.upsert(vectors=vector_data)
            return True
            
        except Exception as e:
            print(f"벡터 저장 실패: {str(e)}")
            return False
            
    def search_vectors(self, 
                      query_vector: List[float],
                      user_id: Optional[str] = None,
                      top_k: int = 5) -> List[Dict]:
        """유사 벡터 검색
        
        Args:
            query_vector: 쿼리 벡터
            user_id: 사용자 ID (None이면 전체 검색)
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        try:
            # 필터 설정
            filter_dict = {}
            if user_id:
                filter_dict["user_id"] = user_id
                
            # 벡터 검색
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            # 결과 포맷팅
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "score": match.score,
                    "metadata": match.metadata
                })
                
            return formatted_results
            
        except Exception as e:
            print(f"벡터 검색 실패: {str(e)}")
            return []
            
    def delete_vectors(self,
                      user_id: str,
                      meeting_date: str,
                      meeting_title: str) -> bool:
        """특정 회의의 벡터 삭제
        
        Args:
            user_id: 사용자 ID
            meeting_date: 회의 날짜
            meeting_title: 회의 제목
            
        Returns:
            삭제 성공 여부
        """
        try:
            # 벡터 삭제
            self.index.delete(filter={
                "user_id": user_id,
                "meeting_date": meeting_date,
                "meeting_title": meeting_title
            })
            
            return True
            
        except Exception as e:
            print(f"벡터 삭제 실패: {str(e)}")
            return False 