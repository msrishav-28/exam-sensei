@echo off
echo ========================================
echo ExamSensei Health Check
echo ========================================
echo.

echo Checking Backend...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running at http://localhost:8000
    curl -s http://localhost:8000/api/v1/health
) else (
    echo [ERROR] Backend is not responding
)

echo.
echo Checking Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is running at http://localhost:3000
) else (
    echo [ERROR] Frontend is not responding
)

echo.
echo Checking API Documentation...
curl -s http://localhost:8000/api/v1/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API Docs available at http://localhost:8000/api/v1/docs
) else (
    echo [ERROR] API Docs not available
)

echo.
echo ========================================
echo Health Check Complete
echo ========================================
pause
