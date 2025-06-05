from flask import Blueprint, jsonify, request
from app.services.rag_service import RAGService

bp = Blueprint("rag_router", __name__, url_prefix="/rag")
rag_service = RAGService()

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
