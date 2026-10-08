@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo    Compilando PinkChan Shimeji APK para Android
echo ==============================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_apk.ps1"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la compilacion del APK.
    pause
    exit /b %errorlevel%
)
echo.
echo [EXITO] APK generado correctamente.
pause
