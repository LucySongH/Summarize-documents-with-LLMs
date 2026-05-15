#!/bin/bash
# stop.sh — Stop DocSum
echo "🛑 Stopping DocSum..."
docker compose down
echo "✅ DocSum stopped."
