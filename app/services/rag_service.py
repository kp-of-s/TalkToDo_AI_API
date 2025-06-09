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
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def process_meeting(self, 
                       segments: List[Dict], 
                       user_id: str, 
                       meeting_date: str) -> Dict:
        """회의 데이터 처리 및 저장
        
        Args:
            segments: 회의 세그먼트 목록
            user_id: 사용자 ID
            meeting_date: 회의 날짜 (YYYY-MM-DD)
            
        Returns:
            처리 결과 (요약, 할일, 일정)
        """
        print("라그 서비스, 세그먼트 넘어온거 확인:", segments)
        print("유저 ID:", user_id)
        print("회의 날짜:", meeting_date)

        try:
            # 1. S3에 저장
            try:
                self.s3_util.save_meeting_segments(
                    segments=segments,
                    user_id=user_id,
                    meeting_date=meeting_date
                )
            except Exception as e:
                print(f"S3 저장 실패: {str(e)}")
                raise Exception("회의록 저장에 실패했습니다.")
            
            # 2. RAG 처리를 위한 청크 생성 및 벡터 DB 저장
            try:
                chunks = self.langchain_util.create_contextual_chunks(segments)
                embeddings = self.embedding_util.process_segments(chunks)
                self.vector_db_util.store_vectors(embeddings, user_id, meeting_date)
            except Exception as e:
                print(f"RAG 처리 실패: {str(e)}")
                raise Exception("회의록 인덱싱에 실패했습니다.")
            
            # 3. 과거 회의록 검색 및 현재 회의록 증강
            try:
                # 현재 회의록의 전체 내용을 임베딩
                current_meeting_text = self._format_segments(segments)
                current_embedding = self.embedding_util.get_embeddings(current_meeting_text)
                
                # 과거 회의록 검색 (현재 회의록 제외)
                search_results = self.vector_db_util.search_vectors(
                    current_embedding,
                    user_id=user_id,
                    top_k=3,
                    exclude_date=meeting_date  # 현재 회의록 제외
                )
                
                # 검색 결과를 포함한 증강된 텍스트 생성
                augmented_text = self._format_segments_with_context(
                    segments=segments,
                    search_results=search_results
                )
            except Exception as e:
                print(f"회의록 증강 실패: {str(e)}")
                # 증강 실패 시 기존에 생성된 텍스트 재사용
                augmented_text = current_meeting_text
            
            # 4. 증강된 텍스트로 요약, 할일, 일정 추출
            try:
                summary = self.bedrock_util.summarize_meeting(augmented_text)
            except Exception as e:
                print(f"요약 생성 실패: {str(e)}")
                summary = {"subject": "", "summary": "요약 생성에 실패했습니다."}
            
            try:
                todos = self.bedrock_util.extract_todos(augmented_text, meeting_date)
            except Exception as e:
                print(f"할일 추출 실패: {str(e)}")
                todos = []
            
            try:
                schedules = self.bedrock_util.extract_schedule(augmented_text, meeting_date)
            except Exception as e:
                print(f"일정 추출 실패: {str(e)}")
                schedules = []
            
            return {
                "segments": segments,
                "summary": summary,
                "todos": todos,
                "schedules": schedules
            }
            
        except Exception as e:
            raise Exception(f"회의 처리 중 오류 발생: {str(e)}")
        
    def _process_rag(self, segments: List[Dict], user_id: str, meeting_date: str):
        """RAG 처리를 위한 백그라운드 작업"""
        try:
            # 1. 컨텍스트 기반 청크 생성
            chunks = self.langchain_util.create_contextual_chunks(segments)
            
            # 2. 각 청크에 대한 프롬프트 증강
            augmented_chunks = []
            for chunk in chunks:
                # 청크의 메타데이터 추출
                speaker = chunk.get("speaker", "Unknown")
                start_time = chunk.get("start", "")
                end_time = chunk.get("end", "")
                text = chunk.get("text", "")
                
                # 프롬프트 증강 - 언어 모델이 컨텍스트를 이해하고 구조화하도록 유도
                augmented_prompt = f"""
                당신은 회의 분석 전문가입니다. 다음 회의 내용을 분석해주세요:

                회의 정보:
                - 화자: {speaker}
                - 시간: {start_time} - {end_time}
                - 날짜: {meeting_date}

                회의 내용:
                {text}

                위 내용을 바탕으로 다음을 수행해주세요:
                1. 이 대화의 주요 맥락과 목적을 파악
                2. 중요한 결정사항이나 액션 아이템 식별
                3. 다른 회의나 프로젝트와의 연관성 분석
                4. 후속 조치가 필요한 사항 정리

                분석 결과는 구조화된 형식으로 제공해주세요.
                """
                
                # 증강된 프롬프트를 청크에 추가
                chunk["augmented_prompt"] = augmented_prompt
                augmented_chunks.append(chunk)
            
            # 3. 임베딩 생성
            embeddings = self.embedding_util.process_segments(augmented_chunks)
            
            # 4. 벡터 DB에 저장
            self.vector_db_util.store_vectors(embeddings, user_id, meeting_date)
            
            print(f"RAG 처리 완료: {len(augmented_chunks)}개의 청크 처리됨")
            
        except Exception as e:
            print(f"RAG 처리 중 오류 발생: {str(e)}")
            
    def __del__(self):
        """ThreadPoolExecutor 정리"""
        self.executor.shutdown(wait=False)
        
    def _format_segments(self, segments: List[Dict]) -> str:
        """회의 세그먼트를 텍스트로 변환
        
        Args:
            segments: 회의 세그먼트 목록
            
        Returns:
            포맷된 회의록 텍스트
        """
        if not segments:
            return ""
            
        formatted_text = [
            "=== 회의 개요 ===",
            f"날짜: {segments[0].get('meeting_date', '')}",
            f"참석자: {', '.join(set(seg.get('speaker', 'Unknown') for seg in segments))}",
            "",
            "=== 회의 내용 ==="
        ]
        
        for segment in segments:
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '').strip()
            if text:
                formatted_text.append(f"{speaker}: {text}")
        
        formatted_text.extend([
            "",
            "=== 분석 가이드 ===",
            "1. 주요 논의 사항과 결정사항을 파악하세요.",
            "2. 할일 항목과 담당자를 식별하세요.",
            "3. 일정과 마감일을 확인하세요."
        ])
        
        return "\n".join(formatted_text)

    def _format_segments_with_context(self, segments: List[Dict], search_results: List[Dict]) -> str:
        """검색 결과를 포함한 증강된 회의록 텍스트 생성
        
        Args:
            segments: 현재 회의 세그먼트
            search_results: 검색된 과거 회의록 결과
            
        Returns:
            증강된 회의록 텍스트
        """
        # 기본 회의록 형식 생성
        formatted_text = self._format_segments(segments)
        
        # 검색 결과가 있는 경우에만 컨텍스트 추가
        if search_results:
            context_section = [
                "",
                "=== 관련 과거 회의록 ==="
            ]
            
            for result in search_results:
                chunk = result["chunk"]
                score = result["score"]
                context_section.extend([
                    f"유사도: {score:.2f}",
                    f"날짜: {chunk.get('meeting_date', '')}",
                    f"화자: {chunk.get('speaker', 'Unknown')}",
                    f"내용: {chunk.get('text', '')}",
                    ""
                ])
            
            formatted_text += "\n" + "\n".join(context_section)
        
        return formatted_text 