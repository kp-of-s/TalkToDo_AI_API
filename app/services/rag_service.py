from typing import List, Dict, Optional
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from app.utils.bedrock_util import BedrockUtil
from app.utils.s3_util import S3Util
from app.utils.embedding_util import EmbeddingUtil
from app.utils.vector_db_util import VectorDBUtil
from app.utils.langchain_util import LangChainUtil

load_dotenv()

class RAGService:
    def __init__(self, 
                 bedrock_util: BedrockUtil, 
                 s3_util: S3Util,
                 embedding_util: EmbeddingUtil,
                 vector_db_util: VectorDBUtil,
                 langchain_util: LangChainUtil):
        self.bedrock_util = bedrock_util
        self.s3_util = s3_util
        self.embedding_util = embedding_util
        self.vector_db_util = vector_db_util
        self.langchain_util = langchain_util
        
    def process_meeting(self, 
                       segments: List[Dict], 
                       user_id: str, 
                       meeting_date: str) -> Dict:
        """회의 데이터 처리 및 저장
        
        Args:
            segments: Whisper-화자분리 통합 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            처리 결과 (저장 경로, 요약, 할일, 일정)
        """
        try:
            # 1. 세그먼트 저장
            path = self.s3_util.save_meeting_segments(
                segments=segments,
                user_id=user_id,
                meeting_date=meeting_date
            )
            
            # 2. 문맥 기반 청크 생성
            chunks = self.langchain_util.create_contextual_chunks(segments)
            
            # 3. 요약/할일/일정 추출
            formatted_text = self._format_segments(segments)
            summary = self.bedrock_util.summarize_meeting(formatted_text)
            todos = self.bedrock_util.extract_todos(formatted_text, meeting_date)
            schedules = self.bedrock_util.extract_schedule(formatted_text, meeting_date)
            
            # 4. 청크별 임베딩 생성 및 벡터 DB 저장
            chunks_with_embeddings = []
            for chunk in chunks:
                # 청크 텍스트에 대한 임베딩 생성
                embedding = self.embedding_util.get_embeddings(chunk["text"])
                if embedding:
                    chunk["embedding"] = embedding
                    chunks_with_embeddings.append(chunk)
            
            meeting_title = self.s3_util._generate_meeting_title(user_id, meeting_date)
            
            if chunks_with_embeddings:
                self.vector_db_util.store_vectors(
                    vectors=chunks_with_embeddings,
                    user_id=user_id,
                    meeting_date=meeting_date,
                    meeting_title=meeting_title
                )
            
            return {
                "path": path,
                "meetingTranscript": formatted_text,
                "meetingSummary": summary,
                "todo": todos,
                "schedule": schedules
            }
            
        except Exception as e:
            print(f"회의 처리 실패: {str(e)}")
            raise
        
    def _format_segments(self, segments: List[Dict]) -> str:
        """세그먼트를 텍스트 형식으로 변환
        
        Args:
            segments: 세그먼트 목록
            
        Returns:
            포맷된 텍스트
        """
        formatted_text = []
        for segment in segments:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"]
            formatted_text.append(f"{speaker}: {text}")
        return "\n".join(formatted_text) 