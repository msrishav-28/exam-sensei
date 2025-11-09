@echo off
REM ============================================================
REM ExamSensei - Complete Setup and Launcher
REM One script to rule them all!
REM ============================================================

setlocal enabledelayedexpansion

REM Color codes for better visibility (Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

:MAIN_MENU
cls
echo ============================================================
echo           %BLUE%ExamSensei - Setup ^& Management%RESET%
echo ============================================================
echo.
echo %GREEN%What would you like to do?%RESET%
echo.
echo  1. %YELLOW%First Time Setup%RESET% - Install all dependencies
echo  2. %YELLOW%Start Application%RESET% - Launch ExamSensei
echo  3. %YELLOW%Health Check%RESET% - Verify all services
echo  4. %YELLOW%Update Dependencies%RESET% - Update packages
echo  5. %YELLOW%Run Tests%RESET% - Execute test suite
echo  6. %YELLOW%Cleanup%RESET% - Stop all services
echo  7. %YELLOW%Docker Setup%RESET% - Run with Docker
echo  8. %YELLOW%Exit%RESET%
echo.
echo ============================================================

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto FIRST_TIME_SETUP
if "%choice%"=="2" goto START_APP
if "%choice%"=="3" goto HEALTH_CHECK
if "%choice%"=="4" goto UPDATE_DEPS
if "%choice%"=="5" goto RUN_TESTS
if "%choice%"=="6" goto CLEANUP
if "%choice%"=="7" goto DOCKER_SETUP
if "%choice%"=="8" goto END

echo %RED%Invalid choice. Please try again.%RESET%
timeout /t 2 /nobreak >nul
goto MAIN_MENU

REM ============================================================
REM FIRST TIME SETUP
REM ============================================================
:FIRST_TIME_SETUP
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           First Time Setup - Installing Everything%RESET%
echo %BLUE%============================================================%RESET%
echo.

REM Check Python installation
echo %YELLOW%[1/7] Checking Python installation...%RESET%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%ERROR: Python is not installed or not in PATH!%RESET%
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    goto MAIN_MENU
)
echo %GREEN%✓ Python found%RESET%
echo.

REM Check Node.js installation
echo %YELLOW%[2/7] Checking Node.js installation...%RESET%
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%ERROR: Node.js is not installed or not in PATH!%RESET%
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    goto MAIN_MENU
)
echo %GREEN%✓ Node.js found%RESET%
echo.

REM Setup Backend
echo %YELLOW%[3/7] Setting up Backend...%RESET%
cd backend

REM Create virtual environment if not exists
if not exist venv (
    echo   Creating Python virtual environment...
    python -m venv venv
    echo   %GREEN%✓ Virtual environment created%RESET%
) else (
    echo   %GREEN%✓ Virtual environment already exists%RESET%
)

REM Activate virtual environment and install dependencies
echo   Installing Python dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo %RED%ERROR: Failed to install Python dependencies!%RESET%
    pause
    goto MAIN_MENU
)
echo   %GREEN%✓ Python dependencies installed%RESET%

REM Initialize database
echo   Initializing database...
if not exist examsensei.db (
    alembic upgrade head
    python seed_data.py
    echo   %GREEN%✓ Database initialized with seed data%RESET%
) else (
    echo   %GREEN%✓ Database already exists%RESET%
)

REM Create .env file if not exists
if not exist .env (
    echo   Creating .env file...
    copy .env.example .env >nul 2>&1
    echo   %GREEN%✓ .env file created%RESET%
) else (
    echo   %GREEN%✓ .env file already exists%RESET%
)

cd ..
echo.

REM Setup Frontend
echo %YELLOW%[4/7] Setting up Frontend...%RESET%
cd frontend

REM Install Node dependencies
if not exist node_modules (
    echo   Installing Node.js dependencies...
    call npm install --legacy-peer-deps --silent
    if %errorlevel% neq 0 (
        echo %RED%ERROR: Failed to install Node dependencies!%RESET%
        pause
        goto MAIN_MENU
    )
    echo   %GREEN%✓ Node.js dependencies installed%RESET%
) else (
    echo   %GREEN%✓ Node modules already exist%RESET%
)

REM Create .env.local file if not exists
if not exist .env.local (
    echo   Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
    echo   %GREEN%✓ .env.local file created%RESET%
) else (
    echo   %GREEN%✓ .env.local file already exists%RESET%
)

cd ..
echo.

REM Create logs directory
echo %YELLOW%[5/7] Creating logs directory...%RESET%
if not exist backend\logs (
    mkdir backend\logs
    echo   %GREEN%✓ Logs directory created%RESET%
) else (
    echo   %GREEN%✓ Logs directory exists%RESET%
)
echo.

REM Check optional services
echo %YELLOW%[6/7] Checking optional services...%RESET%
echo   Checking Redis (optional, for caching)...
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Redis is running%RESET%
) else (
    echo   %YELLOW%⚠ Redis not found (optional - caching disabled)%RESET%
)

echo   Checking Ollama (optional, for AI chatbot)...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Ollama is running%RESET%
) else (
    echo   %YELLOW%⚠ Ollama not found (optional - AI chatbot disabled)%RESET%
    echo   Install from: https://ollama.ai/
)
echo.

echo %YELLOW%[7/7] Verifying installation...%RESET%
timeout /t 2 /nobreak >nul
echo.

echo %GREEN%============================================================%RESET%
echo %GREEN%           Setup Complete! ✓%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo %BLUE%Next steps:%RESET%
echo  1. Start the application: Choose option 2 from main menu
echo  2. Access at: http://localhost:3000
echo  3. API Docs: http://localhost:8000/api/v1/docs
echo.
pause
goto MAIN_MENU

REM ============================================================
REM START APPLICATION
REM ============================================================
:START_APP
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           Starting ExamSensei Application%RESET%
echo %BLUE%============================================================%RESET%
echo.
echo Choose startup mode:
echo.
echo  1. Full Stack (Backend + Frontend) - Recommended
echo  2. Backend Only
echo  3. Frontend Only
echo  4. Docker Compose
echo  5. Back to Main Menu
echo.

set /p start_choice="Enter choice (1-5): "

if "%start_choice%"=="1" goto START_FULL
if "%start_choice%"=="2" goto START_BACKEND
if "%start_choice%"=="3" goto START_FRONTEND
if "%start_choice%"=="4" goto START_DOCKER
if "%start_choice%"=="5" goto MAIN_MENU

echo %RED%Invalid choice.%RESET%
timeout /t 2 /nobreak >nul
goto START_APP

:START_FULL
echo.
echo %YELLOW%Starting Full Stack...%RESET%
echo.

REM Start Backend
echo %YELLOW%[1/2] Starting Backend...%RESET%
cd backend
if not exist venv (
    echo %RED%ERROR: Virtual environment not found!%RESET%
    echo Please run First Time Setup first.
    pause
    cd ..
    goto MAIN_MENU
)

start "ExamSensei Backend" cmd /k "cd /d %cd% && call venv\Scripts\activate && uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000"
echo %GREEN%✓ Backend started at http://localhost:8000%RESET%
cd ..

REM Wait for backend to initialize
echo   Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start Frontend
echo %YELLOW%[2/2] Starting Frontend...%RESET%
cd frontend
if not exist node_modules (
    echo %RED%ERROR: Node modules not found!%RESET%
    echo Please run First Time Setup first.
    pause
    cd ..
    goto MAIN_MENU
)

start "ExamSensei Frontend" cmd /k "cd /d %cd% && npm run dev"
echo %GREEN%✓ Frontend started at http://localhost:3000%RESET%
cd ..

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%           Application Started Successfully! ✓%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo %BLUE%Access Points:%RESET%
echo  • Frontend:     http://localhost:3000
echo  • Backend API:  http://localhost:8000
echo  • API Docs:     http://localhost:8000/api/v1/docs
echo  • Health Check: http://localhost:8000/api/v1/health
echo.
echo %YELLOW%Two new command windows have opened.%RESET%
echo %YELLOW%Close those windows to stop the services.%RESET%
echo.
pause
goto MAIN_MENU

:START_BACKEND
echo.
echo %YELLOW%Starting Backend Only...%RESET%
cd backend
call venv\Scripts\activate
uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000
cd ..
goto MAIN_MENU

:START_FRONTEND
echo.
echo %YELLOW%Starting Frontend Only...%RESET%
cd frontend
npm run dev
cd ..
goto MAIN_MENU

:START_DOCKER
echo.
echo %YELLOW%Starting with Docker Compose...%RESET%
docker-compose up -d
if %errorlevel% neq 0 (
    echo %RED%ERROR: Docker Compose failed!%RESET%
    echo Make sure Docker is installed and running.
    pause
    goto MAIN_MENU
)
echo.
echo %GREEN%✓ Services started with Docker%RESET%
echo.
echo Services available at:
echo  • Frontend: http://localhost:3000
echo  • Backend:  http://localhost:8000
echo.
echo To stop: docker-compose down
pause
goto MAIN_MENU

REM ============================================================
REM HEALTH CHECK
REM ============================================================
:HEALTH_CHECK
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           System Health Check%RESET%
echo %BLUE%============================================================%RESET%
echo.

echo %YELLOW%Checking Backend...%RESET%
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓ Backend is HEALTHY%RESET%
    curl -s http://localhost:8000/api/v1/health
) else (
    echo %RED%✗ Backend is NOT responding%RESET%
    echo   Make sure backend is running on port 8000
)
echo.

echo %YELLOW%Checking Frontend...%RESET%
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓ Frontend is HEALTHY%RESET%
) else (
    echo %RED%✗ Frontend is NOT responding%RESET%
    echo   Make sure frontend is running on port 3000
)
echo.

echo %YELLOW%Checking Database...%RESET%
if exist backend\examsensei.db (
    echo %GREEN%✓ Database file exists%RESET%
) else (
    echo %RED%✗ Database file not found%RESET%
)
echo.

echo %YELLOW%Checking Optional Services...%RESET%
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓ Redis is running%RESET%
) else (
    echo %YELLOW%⚠ Redis not running (optional)%RESET%
)

curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓ Ollama is running%RESET%
) else (
    echo %YELLOW%⚠ Ollama not running (optional)%RESET%
)
echo.

echo %BLUE%============================================================%RESET%
pause
goto MAIN_MENU

REM ============================================================
REM UPDATE DEPENDENCIES
REM ============================================================
:UPDATE_DEPS
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           Update Dependencies%RESET%
echo %BLUE%============================================================%RESET%
echo.
echo What do you want to update?
echo.
echo  1. Backend (Python packages)
echo  2. Frontend (Node packages)
echo  3. Both
echo  4. Back to Main Menu
echo.

set /p update_choice="Enter choice (1-4): "

if "%update_choice%"=="1" goto UPDATE_BACKEND
if "%update_choice%"=="2" goto UPDATE_FRONTEND
if "%update_choice%"=="3" goto UPDATE_BOTH
if "%update_choice%"=="4" goto MAIN_MENU

echo %RED%Invalid choice.%RESET%
timeout /t 2 /nobreak >nul
goto UPDATE_DEPS

:UPDATE_BACKEND
echo.
echo %YELLOW%Updating Backend Dependencies...%RESET%
cd backend
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
echo %GREEN%✓ Backend dependencies updated%RESET%
cd ..
pause
goto MAIN_MENU

:UPDATE_FRONTEND
echo.
echo %YELLOW%Updating Frontend Dependencies...%RESET%
cd frontend
call npm update --legacy-peer-deps
echo %GREEN%✓ Frontend dependencies updated%RESET%
cd ..
pause
goto MAIN_MENU

:UPDATE_BOTH
echo.
echo %YELLOW%Updating All Dependencies...%RESET%
echo.
echo %YELLOW%[1/2] Backend...%RESET%
cd backend
call venv\Scripts\activate
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --upgrade --quiet
echo %GREEN%✓ Backend updated%RESET%
cd ..
echo.
echo %YELLOW%[2/2] Frontend...%RESET%
cd frontend
call npm update --legacy-peer-deps --silent
echo %GREEN%✓ Frontend updated%RESET%
cd ..
echo.
echo %GREEN%✓ All dependencies updated%RESET%
pause
goto MAIN_MENU

REM ============================================================
REM RUN TESTS
REM ============================================================
:RUN_TESTS
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           Running Test Suite%RESET%
echo %BLUE%============================================================%RESET%
echo.

cd backend
if not exist venv (
    echo %RED%ERROR: Backend not set up!%RESET%
    echo Please run First Time Setup first.
    pause
    cd ..
    goto MAIN_MENU
)

echo %YELLOW%Running backend tests...%RESET%
call venv\Scripts\activate
pytest --cov --cov-report=html --cov-report=term
echo.

if %errorlevel% equ 0 (
    echo %GREEN%✓ All tests passed!%RESET%
    echo.
    echo Test coverage report generated at: backend\htmlcov\index.html
) else (
    echo %RED%✗ Some tests failed!%RESET%
)

cd ..
echo.
pause
goto MAIN_MENU

REM ============================================================
REM CLEANUP
REM ============================================================
:CLEANUP
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           Cleanup - Stopping Services%RESET%
echo %BLUE%============================================================%RESET%
echo.
echo %YELLOW%This will stop all running services.%RESET%
echo.
set /p confirm="Continue? (Y/N): "

if /i not "%confirm%"=="Y" goto MAIN_MENU

echo.
echo %YELLOW%Stopping services...%RESET%

REM Kill processes on specific ports
echo   Stopping backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo %GREEN%✓ Backend stopped%RESET%

echo   Stopping frontend (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo %GREEN%✓ Frontend stopped%RESET%

echo   Stopping Docker containers...
docker-compose down >nul 2>&1
echo %GREEN%✓ Docker containers stopped%RESET%

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%           Cleanup Complete! ✓%RESET%
echo %GREEN%============================================================%RESET%
echo.
pause
goto MAIN_MENU

REM ============================================================
REM DOCKER SETUP
REM ============================================================
:DOCKER_SETUP
cls
echo %BLUE%============================================================%RESET%
echo %BLUE%           Docker Setup%RESET%
echo %BLUE%============================================================%RESET%
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%ERROR: Docker is not installed!%RESET%
    echo Please install Docker Desktop from https://www.docker.com/
    pause
    goto MAIN_MENU
)

echo %YELLOW%Building and starting Docker containers...%RESET%
echo.
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo %RED%ERROR: Docker Compose failed!%RESET%
    pause
    goto MAIN_MENU
)

echo.
echo %YELLOW%Initializing database in container...%RESET%
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%           Docker Setup Complete! ✓%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo Services available at:
echo  • Frontend: http://localhost:3000
echo  • Backend:  http://localhost:8000
echo  • API Docs: http://localhost:8000/api/v1/docs
echo.
echo %YELLOW%To stop:%RESET% docker-compose down
echo %YELLOW%To view logs:%RESET% docker-compose logs -f
echo.
pause
goto MAIN_MENU

REM ============================================================
REM END
REM ============================================================
:END
cls
echo.
echo %GREEN%Thank you for using ExamSensei!%RESET%
echo.
echo %BLUE%Visit us at:%RESET% https://github.com/msrishav-28/exam-sensei
echo.
timeout /t 3 /nobreak
exit /b 0
