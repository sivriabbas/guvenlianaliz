@echo off
REM Phase 10: Docker Build and Run Script
REM Build and start all containers

echo ================================================
echo Phase 10: Docker Deployment
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    echo Run: copy .env.example .env
    pause
    exit /b 1
)

echo [1/5] Building Docker image...
docker-compose build --no-cache

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [2/5] Starting containers...
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start containers!
    pause
    exit /b 1
)

echo.
echo [3/5] Waiting for services to be healthy...
timeout /t 10 >nul

echo.
echo [4/5] Checking container status...
docker-compose ps

echo.
echo [5/5] Checking application health...
timeout /t 5 >nul
curl -s http://localhost:8000/api/ml/health

echo.
echo ================================================
echo Deployment Complete!
echo ================================================
echo.
echo Application: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Health:      http://localhost:8000/api/ml/health
echo.
echo View logs:   docker-compose logs -f app
echo Stop:        docker-compose down
echo Restart:     docker-compose restart
echo.

pause
