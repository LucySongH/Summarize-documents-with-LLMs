@echo off
REM start.bat — DocSum launcher for Windows
REM Usage: Double-click or run in Command Prompt

echo ============================================
echo   DocSum — On-Premise Document Summarizer
echo ============================================
echo.

REM Check Docker is running
docker info > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running.
    echo         Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting DocSum...
echo.

REM Start containers
docker compose up -d

echo.
echo Waiting for Ollama to be ready...
timeout /t 10 /nobreak > nul

REM Pull models if not already downloaded
echo Checking models (this may take a while on first run)...
docker exec docsum_ollama ollama pull llama3.2
docker exec docsum_ollama ollama pull phi3
docker exec docsum_ollama ollama pull gemma2:2b

echo.
echo ============================================
echo  DocSum is ready!
echo.
echo   App      : http://localhost:8501
echo   API Docs : http://localhost:8000/docs
echo.
echo   To stop  : stop.bat
echo ============================================
echo.
pause
