@echo off
echo ========================================
echo    Personal Daily Journal App
echo ========================================
echo.

:: Navigate to the correct directory
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

:: Check if TextBlob data is downloaded
echo Checking TextBlob data...
python -c "import nltk; nltk.data.find('tokenizers/punkt')" >nul 2>&1
if errorlevel 1 (
    echo Downloading TextBlob data...
    python -m textblob.download_corpora
)

echo.
echo ========================================
echo    Starting Journal App Server...
echo ========================================
echo.
echo The app will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

:: Start the Flask server
python app.py

pause 