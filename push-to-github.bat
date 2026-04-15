@echo off
REM GitHub Push Script for CSP Sudoku Solver
REM This script automates pushing your code to GitHub

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         CSP SUDOKU SOLVER - GITHUB PUSH AUTOMATION             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

REM Get repository URL from user
set /p REPO_URL="Enter your GitHub repository URL (https://github.com/username/repo.git): "

if "!REPO_URL!"=="" (
    echo ERROR: Repository URL cannot be empty
    pause
    exit /b 1
)

echo.
echo ✓ Repository URL: !REPO_URL!
echo.

REM Add remote repository
echo Adding remote repository...
git remote add origin !REPO_URL! 2>nul
if errorlevel 1 (
    echo Remote already exists. Removing old remote...
    git remote remove origin
    git remote add origin !REPO_URL!
)

REM Branch management
echo Setting main branch...
git branch -M main

REM Push to GitHub
echo.
echo Pushing to GitHub...
echo (You may be prompted for authentication)
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Failed to push to GitHub
    echo Common issues:
    echo   1. Authentication failed - Check your GitHub credentials
    echo   2. Wrong repository URL - Verify URL format
    echo   3. Network issue - Check internet connection
    echo.
    echo For help, see GITHUB_PUSH_GUIDE.txt
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ✓ SUCCESS! CODE PUSHED TO GITHUB             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Your project is now available at: !REPO_URL!
echo.
pause
