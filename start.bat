@echo off
echo ========================================
echo ExamSensei - Quick Start
echo ========================================
echo.

echo Choose startup method:
echo 1. Docker (Recommended - Full Stack)
echo 2. Local Development (Backend + Frontend)
echo 3. Backend Only
echo 4. Frontend Only
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto local
if "%choice%"=="3" goto backend
if "%choice%"=="4" goto frontend

:docker
echo.
echo Starting with Docker Compose...
docker-compose up -d
echo.
echo Services starting...
timeout /t 10 /nobreak >nul
echo.
echo Services Available:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/api/v1/docs
echo.
echo To stop: docker-compose down
goto end

:local
echo.
echo Starting Local Development...
echo.

echo Starting Backend...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
if not exist examsensei.db (
    alembic upgrade head
    python seed_data.py
)
start "Backend" cmd /k "cd /d %cd% && venv\Scripts\activate && uvicorn app_v2:app --reload"
cd ..

timeout /t 3 /nobreak >nul

echo Starting Frontend...
cd frontend
if not exist node_modules (
    call npm install
)
if not exist .env.local (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
)
start "Frontend" cmd /k "cd /d %cd% && npm run dev"
cd ..

echo.
echo Services starting...
timeout /t 5 /nobreak >nul
echo.
echo Services Available:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/api/v1/docs
goto end

:backend
echo.
echo Starting Backend Only...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
if not exist examsensei.db (
    alembic upgrade head
    python seed_data.py
)
uvicorn app_v2:app --reload
goto end

:frontend
echo.
echo Starting Frontend Only...
cd frontend
if not exist node_modules (
    call npm install
)
if not exist .env.local (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1/docs > .env.local
)
npm run dev
goto end

:end
echo.
pause
