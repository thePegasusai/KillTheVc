@echo off
SET DIR=%~dp0
call "%DIR%python\venv\Scripts\activate.bat"
cd "%DIR%game"
python game.py
