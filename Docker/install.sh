#!/bin/bash
# install.sh — DocSum one-time setup for Mac/Linux
# Run this ONCE before using the app for the first time.

echo "============================================"
echo "  DocSum — Installation Setup"
echo "============================================"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi
echo "[OK] Python found."

# ── Check Ollama ──────────────────────────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    echo "[ERROR] Ollama is not installed."
    echo "Please install Ollama from https://ollama.com/download"
    exit 1
fi
echo "[OK] Ollama found."

# ── Install Python packages ───────────────────────────────────────────────────
echo ""
echo "Installing Python packages..."
pip3 install -r requirements.txt
echo "[OK] Python packages installed."

# ── Start Ollama service ──────────────────────────────────────────────────────
echo ""
echo "Starting Ollama service..."
ollama serve &> /dev/null &
sleep 5

# ── Download AI models ────────────────────────────────────────────────────────
echo ""
echo "Downloading AI models (this may take 10-20 minutes on first run)..."
echo ""

echo "Downloading llama3.2..."
ollama pull llama3.2

echo "Downloading phi3..."
ollama pull phi3

echo "Downloading gemma2:2b..."
ollama pull gemma2:2b

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  Installation complete!"
echo ""
echo "  Run ./start.sh to launch the app."
echo "============================================"
