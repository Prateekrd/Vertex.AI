@echo off
echo Starting SIH Harmonization Platform...
start "SIH Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
start "SIH Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo.
echo Both servers are launching in separate windows!
echo - Backend API & Docs: http://localhost:8000/docs
echo - Frontend UI:        http://localhost:3000
echo.
pause
