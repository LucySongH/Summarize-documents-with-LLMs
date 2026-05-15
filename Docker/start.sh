#!/bin/bash
# start.sh — DocSum launcher for Mac/Linux
# Usage: ./start.sh

echo "============================================"
echo "  DocSum — On-Premise Document Summarizer"
echo "============================================"
echo ""

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running."
  echo "   Please start Docker Desktop and try again."
  exit 1
fi

echo "🚀 Starting DocSum..."
echo ""

# Start containers
docker compose up -d

echo ""
echo "⏳ Waiting for Ollama to be ready..."
sleep 10

# Pull models if not already downloaded
echo "📥 Checking models (this may take a while on first run)..."
docker exec docsum_ollama ollama pull llama3.2
docker exec docsum_ollama ollama pull phi3
docker exec docsum_ollama ollama pull gemma2:2b

echo ""
echo "============================================"
echo "✅ DocSum is ready!"
echo ""
echo "  📄 App       → http://localhost:8501"
echo "  🔧 API Docs  → http://localhost:8000/docs"
echo ""
echo "  To stop: ./stop.sh"
echo "============================================"
