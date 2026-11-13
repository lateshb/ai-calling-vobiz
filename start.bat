@echo off
cd /d "%~dp0"
echo Closing any old OutboundAI windows (so only one AI answers each call)...
taskkill /FI "WINDOWTITLE eq OutboundAI Dashboard*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq OutboundAI Agent*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Starting OutboundAI dashboard and agent...
start "OutboundAI Dashboard" cmd /k python -m uvicorn server:app --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak >nul
start "OutboundAI Agent" cmd /k python agent.py start
timeout /t 5 /nobreak >nul
start "" http://localhost:8000
