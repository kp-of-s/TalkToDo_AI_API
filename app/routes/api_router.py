from flask import Blueprint, request, jsonify
import os
from app.services.api_service import APIService
from app.utils.audio_utils import save_audio_file, cleanup_temp_file
from app.utils.whisper_util import WhisperUtil
from app.services.rag_service import RAGService
from app.utils.bedrock_util import BedrockUtil
from app.utils.s3_util import S3Util
from app.utils.embedding_util import EmbeddingUtil
from app.utils.vector_db_util import VectorDBUtil
from app.utils.langchain_util import LangChainUtil

# 유틸리티 인스턴스 초기화
whisper_util = WhisperUtil()
bedrock_util = BedrockUtil()
s3_util = S3Util()
embedding_util = EmbeddingUtil()
vector_db_util = VectorDBUtil()
langchain_util = LangChainUtil()

# RAG 서비스 초기화
rag_service = RAGService(
    bedrock_util=bedrock_util,
    s3_util=s3_util,
    embedding_util=embedding_util,
    vector_db_util=vector_db_util,
    langchain_util=langchain_util
)

# API 서비스 초기화
api_service = APIService(
    whisper_util=whisper_util,
    langchain_util=langchain_util,
    s3_util=s3_util
)

# Blueprint 생성
bp = Blueprint('api', __name__)

# 업로드 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def home():
    return jsonify({"message": "작동댄다아아아아앗"})

@bp.route('/process-meeting', methods=['POST'])
def process_meeting():
    """회의 오디오 파일 처리 API"""
    try:
        # 파일 확인
        if 'audio' not in request.files:
            return jsonify(error="파일이 없습니다."), 400
            
        audio = request.files['audio']
        if audio.filename == '':
            return jsonify(error="선택된 파일이 없습니다."), 400
            
        # 사용자 ID 확인
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify(error="사용자 ID가 필요합니다."), 400
            
        # 회의 날짜 확인
        meeting_date = request.form.get('meeting_date')
        if not meeting_date:
            return jsonify(error="회의 날짜가 필요합니다."), 400

        # 오디오 처리
        result = api_service.process_audio(
            audio_file=audio,
            user_id=user_id,
            meeting_date=meeting_date
        )
        
        return jsonify(**result), 200
        
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        cleanup_temp_file(audio)