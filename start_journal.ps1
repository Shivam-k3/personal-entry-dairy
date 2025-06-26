# Personal Daily Journal App Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Personal Daily Journal App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to the script directory
Set-Location $PSScriptRoot

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    $flaskInstalled = python -c "import flask; print('installed')" 2>$null
    if ($flaskInstalled -ne "installed") {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
    } else {
        Write-Host "✓ Dependencies already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if TextBlob data is downloaded
Write-Host "Checking TextBlob data..." -ForegroundColor Yellow
try {
    $nltkData = python -c "import nltk; nltk.data.find('tokenizers/punkt')" 2>$null
    Write-Host "✓ TextBlob data ready" -ForegroundColor Green
} catch {
    Write-Host "Downloading TextBlob data..." -ForegroundColor Yellow
    python -m textblob.download_corpora
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Starting Journal App Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will be available at:" -ForegroundColor White
Write-Host "  http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask server
python app.py 