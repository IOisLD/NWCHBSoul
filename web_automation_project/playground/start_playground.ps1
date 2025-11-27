# Start Testing Playground — Launches mock API server and opens control panel

$ProjectRoot = "C:\Users\GCS\NWCHBSoul\web_automation_project"
$FixturesDir = "$ProjectRoot\playground\api_fixtures"
$Port = 5000

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Testing Playground Startup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if fixtures directory exists
if (-not (Test-Path $FixturesDir)) {
    Write-Host "ERROR: Fixtures directory not found: $FixturesDir" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Mock API Server on port $Port..." -ForegroundColor Green
Write-Host "Fixtures directory: $FixturesDir" -ForegroundColor Yellow
Write-Host ""

# Start the mock API server
cd $ProjectRoot
python -m scripts.mock_api_server --port $Port --fixtures-dir $FixturesDir --debug

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Server stopped." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
