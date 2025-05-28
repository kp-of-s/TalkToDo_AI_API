@echo off
echo === CUDA 설치 시작 ===

:: CUDA 툴킷 다운로드 및 설치
powershell -Command "& {Invoke-WebRequest -Uri 'https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_522.06_windows.exe' -OutFile 'cuda_installer.exe'}"
cuda_installer.exe -s

:: 환경 변수 설정
setx CUDA_PATH "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8"
setx PATH "%PATH%;%CUDA_PATH%\bin"
setx PATH "%PATH%;%CUDA_PATH%\libnvvp"

:: 설치 확인
echo 설치 확인 중...
nvcc --version
nvidia-smi

echo === CUDA 설치 완료 ===
echo 시스템을 재시작해주세요.
pause 