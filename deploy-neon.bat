@echo off
REM Deploy SOPA Backend to Production with Neon Database
REM This script deploys the application using only Neon cloud database
REM No local PostgreSQL container needed

echo 🚀 SOPA Backend - Deploying to Production with Neon Database
echo ============================================================

REM Check if .env.prod exists
if not exist ".env.prod" (
    echo ❌ Error: .env.prod file not found!
    echo 📝 Please copy .env.prod.example to .env.prod and configure your Neon database URL
    echo    copy .env.prod.example .env.prod
    pause
    exit /b 1
)

echo ✅ Environment configuration found

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.prod.yml down 2>nul

REM Clean up old images (optional)
echo 🧹 Cleaning up old images...
docker rmi sopa-backend_api 2>nul

REM Build and start with Neon
echo 🏗️  Building and starting with Neon database...
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

REM Wait a moment for containers to start
echo ⏳ Waiting for containers to initialize...
timeout /t 10 /nobreak >nul

REM Check container status
echo 🔍 Checking container status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REM Test API connectivity
echo 🌐 Testing API connectivity...
timeout /t 5 /nobreak >nul
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API is responding!
) else (
    echo ⚠️  API may still be starting up. Check logs with:
    echo    docker logs -f sopa_api_prod
)

echo.
echo 🎉 Deployment completed!
echo ================================================
echo 📊 Monitor with:
echo    docker logs -f sopa_api_prod
echo    docker stats
echo.
echo 🔧 Manage database:
echo    docker exec -it sopa_api_prod bash
echo    python scripts/fix_prisma_permissions.py
echo.
echo 🌐 Access API:
echo    http://localhost:8000
echo    http://localhost:8000/docs
echo.
echo 🛑 Stop deployment:
echo    docker-compose -f docker-compose.prod.yml down
echo ================================================

pause
