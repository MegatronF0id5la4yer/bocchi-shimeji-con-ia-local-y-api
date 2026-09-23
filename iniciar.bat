@echo off
title PinkChan Shimeji
echo Iniciando Pink Chan...
pip show pillow >nul 2>&1   || pip install pillow
pip show requests >nul 2>&1 || pip install requests
pip show pywin32 >nul 2>&1  || pip install pywin32
start pythonw PinkChan.pyw
