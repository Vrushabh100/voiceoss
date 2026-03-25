@echo off
echo Starting VoiceOS...

start /B "" "C:\VoiceOS\backend\venv\Scripts\python.exe" "C:\VoiceOS\backend\main.py"
timeout /t 3 /nobreak

start /B "" "C:\VoiceOS\backend\venv\Scripts\python.exe" "C:\VoiceOS\backend\run_agents.py"
timeout /t 2 /nobreak

echo VoiceOS Backend Started!