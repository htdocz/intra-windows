@echo off
title PROJEYI EXE OLARAK DERLE
cd /d "%~dp0"

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Yonetici yetkileri aliniyor...
    powershell -Command "Start-Process cmd -ArgumentList '/c derle.bat' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

echo Eski calisan surecler kapatiliyor...
taskkill /F /IM IntraTurkey.exe >nul 2>&1
taskkill /F /IM intra-windpi.exe >nul 2>&1

echo ========================================================
echo        INTRA TURKEY - EXE DERLEYICI
echo ========================================================
echo.

:: 1. PyInstaller Kurulum Kontrolu
echo [1/5] PyInstaller kontrol ediliyor...
python -c "import PyInstaller" >nul 2>&1
if %errorLevel% neq 0 (
    echo PyInstaller bulunamadi. Yukleniyor...
    pip install pyinstaller
) else (
    echo PyInstaller zaten kurulu.
)
echo.

:: 2. Ikon Uretimi Kontrolu
echo [2/5] Ikon dosyalari kontrol ediliyor...
cd goodbyedpi-gui-win
python -c "import os, sys; sys.path.append(os.getcwd()); from app import ensure_icon_files; ensure_icon_files()" >nul 2>&1
echo Ikonlar hazir.
echo.

:: 3. Derleme Islemi
echo [3/5] PyInstaller ile Tek Dosya (EXE) derleniyor...
echo Bu islem 30 saniye kadar surebilir, lutfen bekleyin...
pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --add-data "bin/intra-windpi.exe;bin" --add-data "icon.png;." --add-data "icon.ico;." --name="IntraWindows" app.py

if %errorLevel% neq 0 (
    echo.
    echo [HATA] Derleme basarisiz oldu! Lutfen hata mesajlarini kontrol edin.
    pause
    exit /b
)
echo.

:: 4. Dosyayi Ana Dizine Tasima
echo [4/5] Derlenen dosya ana dizine tasiniyor...
cd ..
if exist "IntraWindows.exe" del /f "IntraWindows.exe"
move "goodbyedpi-gui-win\dist\IntraWindows.exe" ".\IntraWindows.exe" >nul 2>&1
echo.

:: 5. Temizlik
echo [5/5] Gecici derleme dosyalari temizleniyor...
cd goodbyedpi-gui-win
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1
del /f /q IntraWindows.spec >nul 2>&1
cd ..

echo.
echo ========================================================
echo TEBRIKLER! Tek parca EXE basariyla olusturuldu.
echo Klasorde 'IntraWindows.exe' adinda bulabilirsiniz.
echo ========================================================
echo.
pause
