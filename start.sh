#!/bin/bash
echo ""
echo "+====================================================+"
echo "|  PricePulse - AI-Powered Dynamic Pricing Engine   |"
echo "+====================================================+"
echo ""

# Check Python
python3 --version >/dev/null 2>&1 || { echo "ERROR: Python 3 not found"; exit 1; }

# Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt --quiet

# Initialize
echo "[2/4] Initializing database and ML models..."
python3 app.py

# Backend
echo "[3/4] Starting FastAPI Backend (port 8000)..."
python3 -m uvicorn backend.main:app --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!
sleep 2

# Frontend
echo "[4/4] Starting Streamlit Dashboard (port 8501)..."
streamlit run frontend/dashboard.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "Dashboard: http://localhost:8501"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
