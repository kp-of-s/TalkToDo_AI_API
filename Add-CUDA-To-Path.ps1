# Filename: Add-CUDA-To-Path.ps1

Write-Host "[INFO] CUDA 경로 탐색 중..." -ForegroundColor Cyan

# 기본 CUDA 루트 경로
$cudaRoot = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"

if (-Not (Test-Path $cudaRoot)) {
    Write-Host "[ERROR] CUDA 기본 폴더가 존재하지 않습니다: $cudaRoot" -ForegroundColor Red
    exit 1
}

# 가장 최신 버전 폴더 선택
$cudaVersions = Get-ChildItem -Path $cudaRoot -Directory | Where-Object { $_.Name -like "v*" } | Sort-Object Name -Descending
if ($cudaVersions.Count -eq 0) {
    Write-Host "[ERROR] 설치된 CUDA 버전을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

$latestCudaPath = Join-Path $cudaVersions[0].FullName "bin"
Write-Host "[INFO] 최신 CUDA bin 경로: $latestCudaPath"

if (-Not (Test-Path $latestCudaPath)) {
    Write-Host "[ERROR] CUDA bin 폴더가 존재하지 않습니다: $latestCudaPath" -ForegroundColor Red
    exit 1
}

# 시스템 PATH 환경변수 가져오기
$envPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)

# 이미 등록되었는지 확인
if ($envPath -like "*$latestCudaPath*") {
    Write-Host "[INFO] 이미 PATH에 등록되어 있습니다." -ForegroundColor Green
} else {
    # 등록
    $newPath = "$envPath;$latestCudaPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
    Write-Host "[SUCCESS] CUDA 경로가 PATH에 추가되었습니다." -ForegroundColor Green
}

# 적용을 위해 재시작 필요 안내
Write-Host "`n[NOTE] 변경사항을 적용하려면 시스템을 재시작하거나 로그아웃/로그인 해야 합니다." -ForegroundColor Yellow