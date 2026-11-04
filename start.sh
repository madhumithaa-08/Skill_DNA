#!/usr/bin/env bash
# SKILL DNA — Single-command startup
# Builds the React frontend, then serves everything from FastAPI on port 8000.

# Resolve the project root from wherever this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -e

echo "🧬 SKILL DNA — Starting up..."
echo "   Project root: $SCRIPT_DIR"

# 1. Build React frontend
echo ""
echo "🎨 Building React frontend..."
cd "$SCRIPT_DIR/frontend"
npm run build

# 2. Go back to project root and launch FastAPI
cd "$SCRIPT_DIR"
echo ""
echo "🚀 SKILL DNA running at → http://localhost:8000"
echo "   API docs (FastAPI Swagger) → http://localhost:8000/docs"
echo ""
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
