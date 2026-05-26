@echo off
REM ExamSensei — local dev launcher (no Docker; uses Supabase in cloud)
echo ========================================
echo ExamSensei - Quick Start
echo ========================================
echo.

echo Choose startup method:
echo 1. Backend + Frontend (both)
echo 2. Backend only
echo 3. Frontend only
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto both
if "%choice%"=="2" goto backend
if "%choice%"=="3" goto frontend

:both
call :start_backend
timeout /t 3 /nobreak >nul
call :start_frontend
goto endmsg

:backend
call :start_backend
goto endmsg

:frontend
call :start_frontend
goto endmsg

:start_backend
echo Starting Backend...
pushd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
if not exist .env (
    copy .env.example .env >nul
    echo Created backend\.env from .env.example -- edit it to point at Supabase.
)
start "ExamSensei Backend" cmd /k "cd /d %cd% && venv\Scripts\activate && uvicorn app_v2:app --reload"
popd
exit /b 0

:start_frontend
echo Starting Frontend...
pushd frontend
if not exist node_modules (
    call npm install --legacy-peer-deps
)
if not exist .env.local (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
)
start "ExamSensei Frontend" cmd /k "cd /d %cd% && npm run dev"
popd
exit /b 0

:endmsg
echo.
echo Services starting...
timeout /t 5 /nobreak >nul
echo.
echo Services Available:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/api/v1/docs
echo.
pause
