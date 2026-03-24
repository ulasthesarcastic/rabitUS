#!/bin/bash
# rabitUS — local development startup

set -e

echo "🐇 rabitUS başlatılıyor..."

# Backend
echo "📦 Backend bağımlılıkları kuruluyor..."
cd backend
pip install -r requirements.txt -q
cd ..

echo "🚀 Backend başlatılıyor (port 8000)..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
echo "📦 Frontend bağımlılıkları kuruluyor..."
cd frontend
npm install --silent
echo "🎨 Frontend başlatılıyor (port 3000)..."
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ rabitUS çalışıyor!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
