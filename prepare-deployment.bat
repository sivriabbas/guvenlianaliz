@echo off
REM ================================================
REM NAMECHEAP DEPLOYMENT HELPER
REM FastAPI Projesini Hazırla ve Zip'le
REM ================================================

echo.
echo ================================================
echo   FASTAPI NAMECHEAP DEPLOYMENT PACKAGER
echo ================================================
echo.

REM Deployment klasörü oluştur
if not exist "deploy_package" mkdir deploy_package

echo [1/5] Ana uygulama dosyalarini kopyaliyorum...
copy simple_fastapi.py deploy_package\
copy passenger_wsgi.py deploy_package\
copy .htaccess deploy_package\
copy requirements-namecheap.txt deploy_package\requirements.txt
copy config.yaml deploy_package\

echo [2/5] Python modullerni kopyaliyorum...
copy api_utils.py deploy_package\
copy analysis_logic.py deploy_package\
copy comprehensive_analysis.py deploy_package\
copy elo_utils.py deploy_package\
copy cache_manager.py deploy_package\
copy factor_weights.py deploy_package\
copy data_fetcher.py deploy_package\
copy real_time_data.py deploy_package\
copy injuries_api.py deploy_package\
copy match_importance.py deploy_package\
copy xg_analysis.py deploy_package\
copy weather_api.py deploy_package\
copy referee_analysis.py deploy_package\
copy betting_odds_api.py deploy_package\
copy tactical_analysis.py deploy_package\
copy transfer_impact.py deploy_package\
copy squad_experience.py deploy_package\

echo [3/5] Phase 7-8 modullerni kopyaliyorum...
copy ml_model_manager.py deploy_package\
copy ensemble_predictor.py deploy_package\
copy prediction_logger.py deploy_package\
copy api_security.py deploy_package\
copy request_validation.py deploy_package\
copy api_metrics.py deploy_package\
copy advanced_logging.py deploy_package\
copy api_documentation.py deploy_package\
copy analytics_engine.py deploy_package\
copy report_generator.py deploy_package\
copy oauth2_auth.py deploy_package\
copy jwt_manager.py deploy_package\
copy rbac_manager.py deploy_package\
copy api_versioning.py deploy_package\
copy query_optimizer.py deploy_package\
copy advanced_cache.py deploy_package\
copy compression_middleware.py deploy_package\
copy connection_pool.py deploy_package\

echo [4/5] Klasorleri kopyaliyorum...
xcopy /E /I /Y models deploy_package\models
xcopy /E /I /Y static deploy_package\static
xcopy /E /I /Y templates deploy_package\templates

echo [5/5] .env.example dosyasini olusturuyorum...
(
echo # FASTAPI PRODUCTION ENVIRONMENT
echo.
echo # API Keys
echo API_KEY=your_api_football_key_here
echo.
echo # Environment
echo ENVIRONMENT=production
echo DEBUG=False
echo.
echo # Database ^(cPanel'den doldur^)
echo DB_HOST=localhost
echo DB_NAME=username_analiz_db
echo DB_USER=username_dbuser
echo DB_PASSWORD=strong_password_here
echo DB_PORT=3306
echo.
echo # Security
echo SECRET_KEY=generate_random_secret_key
echo ALLOWED_HOSTS=xn--gvenlinaliz-dlb.com
echo.
echo # Redis ^(Shared hosting'de disable^)
echo REDIS_ENABLED=False
) > deploy_package\.env.example

echo.
echo ================================================
echo   PAKET HAZIRLANDI
echo ================================================
echo.
echo Dosyalar deploy_package\ klasorunde
echo.
echo SONRAKI ADIMLAR:
echo 1. deploy_package\ klasorunu ZIP'le
echo 2. ZIP dosyasini cPanel File Manager'a yukle
echo 3. Extract et
echo 4. SSH ile virtual environment kur
echo 5. .env dosyasini .env.example'dan olustur ve doldur
echo.
echo Detayli talimatlar: NAMECHEAP_FASTAPI_DEPLOYMENT.md
echo.
pause
