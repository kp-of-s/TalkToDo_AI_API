from flask import Flask
from flask_cors import CORS
from app.services.api_service import APIService
from app.services.rag_service import RAGService
from app.utils.whisper_util import WhisperUtil
from app.utils.bedrock_util import BedrockUtil
from app.utils.s3_util import S3Util
from app.routes.api_router import bp as api_bp
from app.routes.rag_router import bp as rag_bp

app = Flask(__name__)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "*"}})

# 의존성 초기화
whisper_util = WhisperUtil()
bedrock_util = BedrockUtil()
s3_util = S3Util()
rag_service = RAGService(bedrock_util, s3_util)
api_service = APIService(
    whisper_util=whisper_util,
    rag_service=rag_service
)

# 라우터 등록
app.register_blueprint(api_bp)
app.register_blueprint(rag_bp)

if __name__ == "__main__":
    app.run(debug=True) 