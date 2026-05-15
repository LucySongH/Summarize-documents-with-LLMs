@echo off
REM start.bat — DocSum launcher for Windows (local mode)
REM Run this every time you want to use the app.

echo ============================================
echo   DocSum — On-Premise Document Summarizer
echo ============================================
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please run install.bat first.
    pause
    exit /b 1
)

REM ── Check Ollama ───────────────────────────────────────────────────────────
ollama --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama not found. Please run install.bat first.
    pause
    exit /b 1
)

REM ── Start Ollama service ───────────────────────────────────────────────────
echo Starting Ollama...
start /B ollama serve
timeout /t 3 /nobreak > nul
echo [OK] Ollama running.

REM ── Start DocSum app ───────────────────────────────────────────────────────
echo Starting DocSum...
echo.
echo ============================================
echo   App is starting...
echo.
echo   Open your browser and go to:
echo   http://localhost:8501
echo.
echo   Press Ctrl+C to stop the app.
echo ============================================
echo.

python run_app.py
