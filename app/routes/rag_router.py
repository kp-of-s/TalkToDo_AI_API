from flask import Blueprint, jsonify, request
from app.services.rag_service import RAGService
from app.utils.bedrock_util import BedrockUtil
from app.utils.s3_util import S3Util
from app.utils.embedding_util import EmbeddingUtil
from app.utils.vector_db_util import VectorDBUtil
from app.utils.langchain_util import LangChainUtil

# 유틸리티 인스턴스 초기화
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

# Blueprint 생성
bp = Blueprint('rag', __name__)

# ✅ 단일 텍스트 기반 요약/할일/일정
@bp.route("/summary", methods=["POST"])
def summarize_text():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "텍스트가 필요합니다."}), 400
    result = rag_service.summarize_text(text)
    return jsonify({"summary": result})


@bp.route("/todos", methods=["POST"])
def extract_todos():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "텍스트가 필요합니다."}), 400
    result = rag_service.extract_todos(text)
    return jsonify({"todos": result})


@bp.route("/schedules", methods=["POST"])
def extract_schedules():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "텍스트가 필요합니다."}), 400
    result = rag_service.extract_schedules(text)
    return jsonify({"schedules": result})


@bp.route("/summary/all", methods=["GET"])
def get_all_summaries():
    results = rag_service.summarize_all_files()
    if not results:
        return jsonify({"error": "S3에서 파일을 찾을 수 없습니다."}), 404
    return jsonify({"summaries": results})


@bp.route("/todos/all", methods=["GET"])
def get_all_todos():
    results = rag_service.generate_todos()
    if not results:
        return jsonify({"error": "S3에서 파일을 찾을 수 없습니다."}), 404
    return jsonify({"todos": results})


@bp.route("/schedules/all", methods=["GET"])
def get_all_schedules():
    results = rag_service.generate_schedules()
    if not results:
        return jsonify({"error": "S3에서 파일을 찾을 수 없습니다."}), 404
    return jsonify({"schedules": results})


@bp.route('/search', methods=['POST'])
def search_meetings():
    """회의 내용 검색 API"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "검색어가 필요합니다."}), 400
            
        query = data['query']
        user_id = data.get('user_id')  # 선택적
        
        results = rag_service.search_meetings(
            query=query,
            user_id=user_id
        )
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
