@echo off
echo.
echo +======================================================+
echo ^|   PricePulse - AI-Powered Dynamic Pricing Engine    ^|
echo +======================================================+
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Install dependencies if needed
echo [1/4] Checking dependencies...
pip install -r requirements.txt --quiet

REM Initialize DB and train models if needed
echo [2/4] Initializing database and ML models...
python app.py

REM Start Backend API
echo [3/4] Starting FastAPI Backend on port 8000...
start "PricePulse-API" cmd /k "python -m uvicorn backend.main:app --port 8000 --host 0.0.0.0"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

REM Start Streamlit Frontend
echo [4/4] Starting Streamlit Dashboard on port 8501...
start "PricePulse-Dashboard" cmd /k "streamlit run frontend/dashboard.py --server.port 8501"

echo.
echo +======================================================+
echo ^|  PricePulse is starting up!                         ^|
echo ^|                                                      ^|
echo ^|  Dashboard:  http://localhost:8501                   ^|
echo ^|  API Docs:   http://localhost:8000/docs              ^|
echo +======================================================+
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8501
