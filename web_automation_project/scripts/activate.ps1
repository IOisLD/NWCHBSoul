# Activate the Python virtual environment for the project

# Set the path to the project root (adjust if needed)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Path to virtual environment Scripts
$VenvActivate = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"

# Check if the virtual environment exists
if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..."
    & $VenvActivate
} else {
    Write-Error "Virtual environment not found at $VenvActivate"
    exit 1
}

# Optional: run main.py with dry-run flag
$MainScript = Join-Path $ProjectRoot "scripts\main.py"

if (Test-Path $MainScript) {
    Write-Host "Running main.py in dry-run mode..."
    python $MainScript --dry-run
} else {
    Write-Warning "main.py not found at $MainScript. You can run it manually after activation."
}
