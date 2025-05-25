from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Hugging Face 토큰 설정
    app.config['HF_TOKEN'] = os.getenv('HF_TOKEN')
    
    # 라우트 등록
    from app.routes import transcribe
    app.register_blueprint(transcribe.bp)
    
    return app 