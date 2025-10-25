@echo off
REM Phase 9 ML API Launcher
REM Start FastAPI server with ML endpoints

echo ================================================
echo Phase 9: Advanced ML ^& AI API Server
echo ================================================
echo.

echo Starting FastAPI server on port 8000...
echo API Documentation: http://localhost:8000/docs
echo ML Endpoints: http://localhost:8000/api/ml/
echo.

REM Start server
python -m uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload

pause
