# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "관리자 권한으로 실행해주세요!"
    Break
}

# 방화벽 규칙 생성
$ruleName = "Flask Server Port 5000"
$port = 5000

# 기존 규칙이 있다면 제거
Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

# 새로운 방화벽 규칙 생성
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -LocalPort $port `
    -Protocol TCP `
    -Action Allow `
    -Profile Any

Write-Host "방화벽 규칙이 생성되었습니다."

# UPnP를 통한 포트포워딩 설정
# UPnP 라이브러리 설치 확인
if (-not (Get-Package -Name "UPnP" -ErrorAction SilentlyContinue)) {
    Write-Host "UPnP 라이브러리 설치 중..."
    Install-Package -Name "UPnP" -Force
}

# UPnP를 통한 포트포워딩 설정
$upnp = New-Object -ComObject UPnP.UPnPDeviceFinder
$devices = $upnp.FindByType("urn:schemas-upnp-org:device:InternetGatewayDevice:1", 0)

if ($devices.Count -gt 0) {
    $device = $devices.Item(0)
    $service = $device.Services.Item("urn:schemas-upnp-org:service:WANIPConnection:1")
    
    # 기존 포트포워딩 제거
    $service.DeletePortMapping($port, "TCP")
    
    # 새로운 포트포워딩 추가
    $service.AddPortMapping($port, "TCP", $port, $env:COMPUTERNAME, $true, "Flask Server")
    Write-Host "포트포워딩이 설정되었습니다."
} else {
    Write-Warning "UPnP 지원 공유기를 찾을 수 없습니다. 수동으로 포트포워딩을 설정해주세요."
}

Write-Host "설정이 완료되었습니다. 서버를 실행하려면 'python app/run.py'를 실행하세요." 