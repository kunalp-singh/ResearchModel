# Restart Flask Script
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "  SecurNet Flask Server Restart Script" -ForegroundColor Yellow
Write-Host ("="*70) -ForegroundColor Cyan

# Kill all Python processes
Write-Host "`n[1/4] Stopping all Python processes..." -ForegroundColor Green
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verify they're stopped
$pythonProcs = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "    Warning: Some Python processes still running!" -ForegroundColor Red
    $pythonProcs | Format-Table Id, ProcessName, Path
} else {
    Write-Host "    ✓ All Python processes stopped" -ForegroundColor Green
}

# Check port 5000
Write-Host "`n[2/4] Checking port 5000..." -ForegroundColor Green
$portCheck = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "    Warning: Port 5000 still in use!" -ForegroundColor Red
    Start-Sleep -Seconds 3
} else {
    Write-Host "    ✓ Port 5000 is free" -ForegroundColor Green
}

# Change to project directory
Write-Host "`n[3/4] Changing to project directory..." -ForegroundColor Green
Set-Location "c:\Users\asus\Downloads\Epics\SecurNet---An-EPICS-Project-main"
Write-Host "    ✓ Current directory: $PWD" -ForegroundColor Green

# Start Flask
Write-Host "`n[4/4] Starting Flask with Waitress..." -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

$env:PYTHONUNBUFFERED = "1"
& "C:\Users\asus\Downloads\Epics\.venv\Scripts\python.exe" flask_app.py
