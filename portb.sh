#!/bin/bash
# =============================================================================
# PINKCHAN SHIMEJI - PORT B (ANDROID 8.0 TO 15+) LAUNCHER
# Para Termux o terminales Android
# =============================================================================

echo "[*] Iniciando PinkChan Shimeji Port B para Android..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 no encontrado. Intentando instalar vía pkg..."
    pkg update -y && pkg install -y python
fi

# Iniciar servidor y companion
python3 portb.py
