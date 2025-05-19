from flask import Flask, request, jsonify
from flask_cors import CORS
import whisperx
import torch
import tempfile
import os
from app import create_app

app = create_app()
CORS(app)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = whisperx.load_model("large-v2", device)

@app.route('/')
def home():
    return jsonify({"message": "WhisperX 음성-텍스트 변환 API 서버입니다."})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "audio 파일이 필요합니다."}), 400
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        audio_file.save(tmp.name)
        audio_path = tmp.name
    try:
        result = model.transcribe(audio_path)
        text = result["text"]
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(audio_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 