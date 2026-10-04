@echo off
setlocal enabledelayedexpansion
title Bocchi-chan Shimeji
cd /d "%~dp0"
chcp 65001 >nul 2>&1

echo ====================================================
echo           [ BOCCHI-CHAN SHIMEJI LAUNCHER ]
echo ====================================================

:: 0. Si existe el ejecutable compilado, iniciarlo directamente
if exist "%~dp0PinkChan.exe" (
    echo [*] Iniciando Bocchi-chan (Ejecutable standalone)...
    start "" "%~dp0PinkChan.exe"
    exit /b 0
)

:: 1. Detect Python executable
set "PY_CMD="
set "PYW_CMD="

where py.exe >nul 2>&1
if !errorlevel! equ 0 (
    set "PY_CMD=py"
    where pyw.exe >nul 2>&1 && set "PYW_CMD=pyw"
)

if not defined PY_CMD (
    where python.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_CMD=python"
        where pythonw.exe >nul 2>&1 && set "PYW_CMD=pythonw"
    )
)

if not defined PY_CMD (
    where python3.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_CMD=python3"
        where pythonw3.exe >nul 2>&1 && set "PYW_CMD=pythonw3"
    )
)

if not defined PY_CMD (
    echo [ERROR] No se encontro Python ni PinkChan.exe en este equipo.
    echo Por favor descarga e instala Python desde: https://www.python.org/
    echo Asegurate de marcar la casilla: [x] Add Python to PATH al instalar.
    echo.
    pause
    exit /b 1
)

:: 2. Check and install dependencies
echo [*] Verificando dependencias de Python...
!PY_CMD! -m pip show pillow >nul 2>&1
if !errorlevel! neq 0 (
    echo [+] Instalando Pillow...
    !PY_CMD! -m pip install --quiet pillow
)

!PY_CMD! -m pip show requests >nul 2>&1
if !errorlevel! neq 0 (
    echo [+] Instalando Requests...
    !PY_CMD! -m pip install --quiet requests
)

!PY_CMD! -m pip show pywin32 >nul 2>&1
if !errorlevel! neq 0 (
    echo [+] Instalando pywin32...
    !PY_CMD! -m pip install --quiet pywin32
)

:: 3. Launch PinkChan.pyw without console window if possible
echo [*] Iniciando a Bocchi-chan...
if defined PYW_CMD (
    start "" !PYW_CMD! "%~dp0PinkChan.pyw"
) else (
    start "" !PY_CMD! "%~dp0PinkChan.pyw"
)

exit /b 0

