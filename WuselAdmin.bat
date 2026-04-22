@echo off
title WuselMap Admin Starter
echo ⚙️ Aktiviere Umgebung und starte Admin-Zentrale...

:: Falls dein Venv-Ordner "venv" heißt, wird er hier aktiviert:
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

streamlit run admin_app.py --server.port 8502
pause