#!/usr/bin/env pwsh
# GitHub Push Script for CSP Sudoku Solver
# PowerShell version - Run in PowerShell

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         CSP SUDOKU SOLVER - GITHUB PUSH AUTOMATION             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get repository URL from user
$repoUrl = Read-Host "Enter your GitHub repository URL (https://github.com/username/repo.git)"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "ERROR: Repository URL cannot be empty" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✓ Repository URL: $repoUrl" -ForegroundColor Green
Write-Host ""

# Add remote repository
Write-Host "Adding remote repository..." -ForegroundColor Yellow
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0 -and $existingRemote -ne $repoUrl) {
    Write-Host "Remote already exists. Removing old remote..." -ForegroundColor Yellow
    git remote remove origin
}
git remote add origin $repoUrl 2>$null

# Branch management
Write-Host "Setting main branch..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "(You may be prompted for authentication)" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Authentication failed - Check your GitHub credentials" -ForegroundColor Yellow
    Write-Host "  2. Wrong repository URL - Verify URL format" -ForegroundColor Yellow
    Write-Host "  3. Network issue - Check internet connection" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For help, see GITHUB_PUSH_GUIDE.txt" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   ✓ SUCCESS! CODE PUSHED TO GITHUB             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Your project is now available at: $repoUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Visit your repository on GitHub" -ForegroundColor Cyan
Write-Host "  2. Enable GitHub Pages in Settings (optional)" -ForegroundColor Cyan
Write-Host "  3. Share the link with others!" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
