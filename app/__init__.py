from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os



# .env 파일 로드
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 환경 변수 설정
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 라우터 등록
    from app.routes.api_router import bp
    from app.routes.rag_router import bp as rag_bp
    
    app.register_blueprint(bp)
    app.register_blueprint(rag_bp, url_prefix='/rag')
    
    return app 

