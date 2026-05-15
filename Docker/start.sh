#!/bin/bash
# start.sh — DocSum launcher for Mac/Linux (local mode)
# Run this every time you want to use the app.

echo "============================================"
echo "  DocSum — On-Premise Document Summarizer"
echo "============================================"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found. Please run ./install.sh first."
    exit 1
fi

# ── Check Ollama ──────────────────────────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    echo "[ERROR] Ollama not found. Please run ./install.sh first."
    exit 1
fi

# ── Start Ollama service ──────────────────────────────────────────────────────
echo "Starting Ollama..."
ollama serve &> /dev/null &
sleep 3
echo "[OK] Ollama running."

# ── Start DocSum app ──────────────────────────────────────────────────────────
echo "Starting DocSum..."
echo ""
echo "============================================"
echo "  App is starting..."
echo ""
echo "  Open your browser and go to:"
echo "  http://localhost:8501"
echo ""
echo "  Press Ctrl+C to stop the app."
echo "============================================"
echo ""

python3 run_app.py
