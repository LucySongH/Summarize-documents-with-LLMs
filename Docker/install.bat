@echo off
REM install.bat — DocSum one-time setup for Windows
REM Run this ONCE before using the app for the first time.

echo ============================================
echo   DocSum — Installation Setup
echo ============================================
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo Then run this file again.
    pause
    exit /b 1
)
echo [OK] Python found.

REM ── Check Ollama ───────────────────────────────────────────────────────────
ollama --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed.
    echo.
    echo Please install Ollama from https://ollama.com/download
    echo Then run this file again.
    pause
    exit /b 1
)
echo [OK] Ollama found.

REM ── Install Python packages ────────────────────────────────────────────────
echo.
echo Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install packages.
    echo Try running: pip install -r requirements.txt manually.
    pause
    exit /b 1
)
echo [OK] Python packages installed.

REM ── Start Ollama service ───────────────────────────────────────────────────
echo.
echo Starting Ollama service...
start /B ollama serve
timeout /t 5 /nobreak > nul

REM ── Download AI models ─────────────────────────────────────────────────────
echo.
echo Downloading AI models (this may take 10-20 minutes on first run)...
echo Each model is approximately 2GB. Please wait.
echo.

echo Downloading llama3.2...
ollama pull llama3.2

echo Downloading phi3...
ollama pull phi3

echo Downloading gemma2:2b...
ollama pull gemma2:2b

REM ── Done ───────────────────────────────────────────────────────────────────
echo.
echo ============================================
echo   Installation complete!
echo.
echo   Run start.bat to launch the app.
echo ============================================
echo.
pause
