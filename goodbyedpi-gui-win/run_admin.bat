@echo off
title Jigsaw Intra Windows Shield Launcher
cd /d "%~dp0"

:: Check if python is in PATH and is not the WindowsApps store alias
where python >tmp_path.txt 2>&1
set /p PYTHON_PATH=<tmp_path.txt
del tmp_path.txt

:: Check if path contains WindowsApps
echo %PYTHON_PATH% | findstr /i "WindowsApps" >nul
if %errorLevel% neq 0 (
    where python >nul 2>&1
    if %errorLevel% == 0 (
        set "PYTHON_EXE=python"
        goto :launch
    )
)

:: Try to find Python in AppData (standard user install)
for /d %%d in ("%USERPROFILE%\AppData\Local\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        set "PYTHON_EXE=%%d\python.exe"
        goto :launch
    )
)

:: Try to find Python in Program Files (system-wide install)
for /d %%d in ("C:\Program Files\Python\Python*") do (
    if exist "%%d\python.exe" (
        set "PYTHON_EXE=%%d\python.exe"
        goto :launch
    )
)

:: Try to find Python in Microsoft Store path
if exist "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe"
    goto :launch
)

:: Default fallback
set "PYTHON_EXE=python"

:launch
"%PYTHON_EXE%" app.py
if %errorLevel% neq 0 (
    echo.
    echo [HATA] Uygulama calisirken bir hata olustu. Hata kodu (Exit Code): %errorLevel%
    echo.
    pause
)
exit /b
