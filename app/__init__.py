from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 라우트 등록
    from app.routes import transcribe
    app.register_blueprint(transcribe.bp)
    
    return app 