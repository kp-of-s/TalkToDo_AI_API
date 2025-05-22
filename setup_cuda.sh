#!/bin/bash

echo "=== CUDA 설치 시작 ==="

# NVIDIA 드라이버 설치
echo "NVIDIA 드라이버 설치 중..."
sudo apt-get update
sudo apt-get install -y nvidia-driver-525

# CUDA 툴킷 설치
echo "CUDA 툴킷 설치 중..."
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run --silent --driver --toolkit --samples --run-nvidia-xconfig

# 환경 변수 설정
echo "환경 변수 설정 중..."
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 설치 확인
echo "설치 확인 중..."
nvcc --version
nvidia-smi

echo "=== CUDA 설치 완료 ==="
echo "시스템을 재시작해주세요: sudo reboot" 