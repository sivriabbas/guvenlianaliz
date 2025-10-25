@echo off
REM Phase 10: Docker Quick Commands
REM Useful Docker commands for management

:menu
cls
echo ================================================
echo Docker Management Menu
echo ================================================
echo.
echo 1. Start containers
echo 2. Stop containers
echo 3. Restart containers
echo 4. View logs (all)
echo 5. View app logs only
echo 6. Check container status
echo 7. Shell into app container
echo 8. Clean up (remove containers)
echo 9. Full cleanup (remove volumes too)
echo 0. Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto logs_all
if "%choice%"=="5" goto logs_app
if "%choice%"=="6" goto status
if "%choice%"=="7" goto shell
if "%choice%"=="8" goto cleanup
if "%choice%"=="9" goto full_cleanup
if "%choice%"=="0" goto exit

echo Invalid choice!
timeout /t 2 >nul
goto menu

:start
echo Starting containers...
docker-compose up -d
echo.
pause
goto menu

:stop
echo Stopping containers...
docker-compose down
echo.
pause
goto menu

:restart
echo Restarting containers...
docker-compose restart
echo.
pause
goto menu

:logs_all
echo Showing all logs (Ctrl+C to exit)...
docker-compose logs -f
goto menu

:logs_app
echo Showing app logs (Ctrl+C to exit)...
docker-compose logs -f app
goto menu

:status
echo Container status:
docker-compose ps
echo.
echo Health check:
curl -s http://localhost:8000/api/ml/health
echo.
pause
goto menu

:shell
echo Opening shell in app container...
docker-compose exec app /bin/bash
goto menu

:cleanup
echo Removing containers...
docker-compose down
echo Done!
pause
goto menu

:full_cleanup
echo WARNING: This will remove all data!
set /p confirm="Are you sure? (yes/no): "
if not "%confirm%"=="yes" goto menu
echo Removing containers and volumes...
docker-compose down -v
echo Done!
pause
goto menu

:exit
echo Goodbye!
timeout /t 1 >nul
exit /b 0
