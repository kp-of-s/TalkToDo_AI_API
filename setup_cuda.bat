@echo off
setlocal enabledelayedexpansion

echo === CUDA setup start ===

:: NVIDIA 드라이버 확인
echo NVIDIA driver check...
nvidia-smi
if %ERRORLEVEL% NEQ 0 (
    echo NVIDIA driver is not installed.
    echo Please install the driver from https://www.nvidia.com/Download/index.aspx
    pause
    exit /b 1
)

:: 시스템 요구사항 확인
echo System requirements check...
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"

:: CUDA 설치 확인 및 버전 가져오기
echo Checking CUDA installation...
for /f "tokens=3" %%i in ('nvcc --version 2^>^&1 ^| findstr "release"') do set CUDA_VERSION=%%i
if "%CUDA_VERSION%"=="" (
    echo CUDA is not properly installed.
    echo Please install CUDA from: https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local
    pause
    exit /b 1
)

echo Detected CUDA version: %CUDA_VERSION%

:: 환경 변수 설정
echo Setting up environment variables...
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v%CUDA_VERSION%
setx CUDA_PATH "%CUDA_PATH%"
setx PATH "%PATH%;%CUDA_PATH%\bin"
setx PATH "%PATH%;%CUDA_PATH%\libnvvp"

:: PyTorch CUDA 지원 확인
echo Checking PyTorch CUDA support...
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

echo === CUDA setup complete ===
echo Please restart the system to apply environment variable changes.
pause 