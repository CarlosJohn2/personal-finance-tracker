@echo off
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
.venv\Scripts\python.exe -m src.cli.main %*
