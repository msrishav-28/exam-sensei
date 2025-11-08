@echo off
echo ========================================
echo ExamSensei - Update Dependencies
echo ========================================
echo.

echo Choose what to update:
echo 1. Backend Only
echo 2. Frontend Only
echo 3. Both (Recommended)
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both

:backend
echo.
echo Updating Backend Dependencies...
cd backend

echo - Activating virtual environment...
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate

echo - Upgrading pip...
python -m pip install --upgrade pip

echo - Installing updated dependencies...
pip install -r requirements.txt --upgrade

echo - Verifying installation...
pip list

echo.
echo Backend dependencies updated successfully!
cd ..
goto end

:frontend
echo.
echo Updating Frontend Dependencies...
cd frontend

echo - Removing old node_modules and lock file...
if exist node_modules (
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)

echo - Installing updated dependencies...
call npm install

echo - Verifying installation...
call npm list --depth=0

echo.
echo Frontend dependencies updated successfully!
cd ..
goto end

:both
echo.
echo Updating Both Backend and Frontend...
echo.

echo [1/2] Backend Dependencies...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
cd ..

echo.
echo [2/2] Frontend Dependencies...
cd frontend
if exist node_modules (
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)
call npm install
cd ..

echo.
echo ========================================
echo All dependencies updated successfully!
echo ========================================
goto end

:end
echo.
echo Next steps:
echo 1. Test the application: start.bat
echo 2. Run tests: cd backend ^&^& pytest
echo 3. Check for issues: health_check.bat
echo.
pause
