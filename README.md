# WhisperX 기반 음성-텍스트 변환 Flask API

## 소개
이 서버는 WhisperX를 활용하여 음성 파일을 텍스트로 변환하는 API를 제공합니다.

## 설치 방법

### 로컬 개발 환경
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

### Docker 환경
1. Docker 이미지 빌드
```bash
docker-compose build
```

2. 컨테이너 실행
```bash
docker-compose up -d
```

## 실행 방법
### 로컬
```bash
python app.py
```

### Docker
```bash
docker-compose up -d
```

## 주의사항
- 최초 실행 시 WhisperX 모델 파일을 다운로드합니다
- 다운로드는 사용자의 홈 디렉토리 `.cache/huggingface/hub`에 저장됩니다
- 다른 컴퓨터에서 실행할 경우 모델을 다시 다운로드해야 합니다

## API 엔드포인트
- POST `/transcribe` : 음성 파일을 텍스트로 변환
  - form-data로 `audio` 파일 업로드
  - 응답: 변환된 텍스트