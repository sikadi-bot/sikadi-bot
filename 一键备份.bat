@echo off
setlocal
set "PY=C:\Python314\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0sync.py"
echo.
pause
