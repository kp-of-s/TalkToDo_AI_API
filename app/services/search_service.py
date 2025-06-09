from typing import List, Dict, Optional
from app.utils.embedding_util import EmbeddingUtil
from app.utils.vector_db_util import VectorDBUtil

class SearchService:
    def __init__(self, 
                 embedding_util: EmbeddingUtil,
                 vector_db_util: VectorDBUtil):
        self.embedding_util = embedding_util
        self.vector_db_util = vector_db_util
        
    def search_meetings(self, 
                       query: str,
                       user_id: Optional[str] = None,
                       top_k: int = 5) -> List[Dict]:
        """회의 내용 검색
        
        Args:
            query: 검색어
            user_id: 사용자 ID (None이면 전체 검색)
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        try:
            # 1. 쿼리 임베딩 생성
            query_vector = self.embedding_util.get_embeddings(query)
            if not query_vector:
                return []
                
            # 2. 벡터 DB에서 검색
            results = self.vector_db_util.search_vectors(
                query_vector=query_vector,
                user_id=user_id,
                top_k=top_k
            )
            
            # 3. 결과 후처리
            return self._process_search_results(results)
            
        except Exception as e:
            print(f"검색 실패: {str(e)}")
            return []
            
    def _process_search_results(self, results: List[Dict]) -> List[Dict]:
        """검색 결과 후처리
        
        Args:
            results: 검색 결과 목록
            
        Returns:
            후처리된 검색 결과
        """
        processed_results = []
        
        for result in results:
            metadata = result["metadata"]
            processed_results.append({
                "score": result["score"],
                "text": metadata["text"],
                "speaker": metadata["speaker"],
                "meeting_date": metadata["meeting_date"],
                "meeting_title": metadata["meeting_title"],
                "start_time": metadata["start"],
                "end_time": metadata["end"]
            })
            
        return processed_results 