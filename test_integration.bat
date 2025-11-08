@echo off
echo ========================================
echo ExamSensei Integration Test
echo ========================================
echo.

echo Step 1: Checking Backend...
cd backend

echo - Checking if virtual environment exists...
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)

echo - Activating virtual environment...
call venv\Scripts\activate

echo - Installing backend dependencies...
pip install -r requirements.txt --quiet

echo - Checking database...
if not exist examsensei.db (
    echo   Initializing database...
    alembic upgrade head
    python seed_data.py
) else (
    echo   Database exists
)

echo - Starting backend server...
start "ExamSensei Backend" cmd /k "cd /d %cd% && venv\Scripts\activate && uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000"

echo   Backend starting at http://localhost:8000
timeout /t 5 /nobreak >nul

cd ..

echo.
echo Step 2: Checking Frontend...
cd frontend

echo - Checking if node_modules exists...
if not exist node_modules (
    echo   Installing frontend dependencies...
    call npm install
) else (
    echo   Dependencies already installed
)

echo - Checking environment file...
if not exist .env.local (
    echo   Creating .env.local...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
)

echo - Starting frontend server...
start "ExamSensei Frontend" cmd /k "cd /d %cd% && npm run dev"

echo   Frontend starting at http://localhost:3000
timeout /t 5 /nobreak >nul

cd ..

echo.
echo ========================================
echo Integration Test Complete!
echo ========================================
echo.
echo Services Running:
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/api/v1/docs
echo - Frontend: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop services
echo.
pause
