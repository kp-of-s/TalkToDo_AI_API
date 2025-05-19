# WhisperX 기반 음성-텍스트 변환 Flask API

## 소개
이 서버는 WhisperX를 활용하여 음성 파일을 텍스트로 변환하는 API를 제공합니다.

## 설치 방법

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

## 실행 방법
```bash
python app.py
```

## API 엔드포인트
- POST `/transcribe` : 음성 파일을 텍스트로 변환
  - form-data로 `audio` 파일 업로드
  - 응답: 변환된 텍스트