@echo off
echo ========================================
echo ExamSensei Codebase Cleanup Script
echo ========================================
echo.

echo Phase 1: Backing up and replacing modern UI files...
cd frontend

echo - Replacing package.json...
if exist package.json (
    move /Y package.json package.json.backup
)
if exist package.json.new (
    move /Y package.json.new package.json
    echo   ✓ package.json updated
)

echo - Replacing landing page...
if exist src\app\page.tsx (
    move /Y src\app\page.tsx src\app\page.backup
)
if exist src\app\page_modern.tsx (
    move /Y src\app\page_modern.tsx src\app\page.tsx
    echo   ✓ Landing page updated
)

echo - Replacing dashboard...
if exist src\app\dashboard\page.tsx (
    move /Y src\app\dashboard\page.tsx src\app\dashboard\page.backup
)
if exist src\app\dashboard\page_modern.tsx (
    move /Y src\app\dashboard\page_modern.tsx src\app\dashboard\page.tsx
    echo   ✓ Dashboard updated
)

echo - Replacing login page...
if exist src\app\auth\login\page.tsx (
    move /Y src\app\auth\login\page.tsx src\app\auth\login\page.backup
)
if exist src\app\auth\login\page_modern.tsx (
    move /Y src\app\auth\login\page_modern.tsx src\app\auth\login\page.tsx
    echo   ✓ Login page updated
)

echo.
echo Phase 2: Removing old backup files...

if exist src\app\page_old.tsx (
    del /F src\app\page_old.tsx
    echo   ✓ Removed page_old.tsx
)

if exist src\app\page.backup (
    del /F src\app\page.backup
    echo   ✓ Removed page.backup
)

if exist src\app\dashboard\page.backup (
    del /F src\app\dashboard\page.backup
    echo   ✓ Removed dashboard page.backup
)

if exist src\app\auth\login\page.backup (
    del /F src\app\auth\login\page.backup
    echo   ✓ Removed login page.backup
)

if exist package.json.backup (
    del /F package.json.backup
    echo   ✓ Removed package.json.backup
)

cd ..

echo.
echo Phase 3: Backend cleanup...
cd backend

if exist app.py (
    del /F app.py
    echo   ✓ Removed old app.py
)

cd ..

echo.
echo Phase 4: Root directory cleanup...

if exist MODERN_UI_UPGRADE.md (
    move /Y MODERN_UI_UPGRADE.md docs\UI_GUIDE.md
    echo   ✓ Moved UI guide to docs/
)

if exist DOCUMENTATION_SUMMARY.md (
    del /F DOCUMENTATION_SUMMARY.md
    echo   ✓ Removed DOCUMENTATION_SUMMARY.md
)

if exist FINAL_REPORT.md (
    del /F FINAL_REPORT.md
    echo   ✓ Removed FINAL_REPORT.md
)

echo.
echo ========================================
echo Cleanup Complete! ✓
echo ========================================
echo.
echo Next steps:
echo 1. cd frontend
echo 2. npm install
echo 3. npm run dev
echo.
echo See CLEANUP_REPORT.md for details.
pause
