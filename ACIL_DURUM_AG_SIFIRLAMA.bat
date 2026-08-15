@echo off
title ACIL DURUM AG SIFIRLAYICI
cd /d "%~dp0"

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Yonetici yetkileri aliniyor...
    powershell -Command "Start-Process cmd -ArgumentList '/c ACIL_DURUM_AG_SIFIRLAMA.bat' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

echo ========================================================
echo        ACIL DURUM AG AYARLARI SIFIRLAYICI
echo ========================================================
echo.
echo 1. Sistem Proxy ayarlari devre disi birakiliyor...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul 2>&1
netsh winhttp reset proxy >nul 2>&1

echo 2. Ag kartlarinin DNS ayarlari otomatik (DHCP) yapiliyor...
powershell -Command "Get-NetAdapter | Where-Object Status -eq Up | Set-DnsClientServerAddress -ResetServerAddress"

echo 3. DNS Onbellegi temizleniyor...
ipconfig /flushdns >nul 2>&1

echo.
echo ========================================================
echo  ISLEM TAMAMLANDI! Internet baglantiniz normale dondu.
echo ========================================================
echo.
pause
