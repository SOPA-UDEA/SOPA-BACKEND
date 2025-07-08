@echo off
setlocal enabledelayedexpansion

if "%1"=="help" goto help
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
if "%1"=="migrate" goto migrate
if "%1"=="test" goto test
if "%1"=="rebuild" goto rebuild
if "%1"=="seed" goto seed
if "%1"=="reset-seed" goto reset_seed

:help
echo SOPA Docker Management Script
echo.
echo Usage: docker-manager.bat [command]
echo.
echo Commands:
echo   help        Show this help message
echo   dev         Start development environment
echo   prod        Start production environment
echo   stop        Stop all services
echo   clean       Clean up containers and volumes
echo   logs        View application logs
echo   migrate     Run database migrations
echo   test        Run tests in container
echo   rebuild     Clean rebuild development environment
echo   seed        Force run database seeding
echo   reset-seed  Reset seeding flag to allow re-seeding
echo.
goto end

:dev
echo Starting development environment...
docker-compose -f docker-compose.dev.yml up -d
echo.
echo Development environment started!
echo API: http://localhost:8000
echo Database: localhost:5432
echo Redis: localhost:6379
echo.
echo Use 'docker-manager.bat logs' to view logs
goto end

:prod
echo Starting production environment...
if not exist .env.prod (
    echo Error: .env.prod file not found!
    echo Please copy .env.prod.example to .env.prod and configure it.
    goto end
)
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
echo.
echo Production environment started!
goto end

:stop
echo Stopping all services...
docker-compose -f docker-compose.dev.yml down 2>nul
docker-compose -f docker-compose.prod.yml down 2>nul
echo All services stopped!
goto end

:clean
echo Cleaning up Docker resources...
docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>nul
docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>nul
docker system prune -f
echo Cleanup complete!
goto end

:logs
echo Showing application logs...
docker-compose -f docker-compose.dev.yml logs -f api
goto end

:migrate
echo Running database migrations...
docker-compose -f docker-compose.dev.yml exec api prisma migrate dev --name %2
goto end

:test
echo Running tests...
docker-compose -f docker-compose.dev.yml exec api pytest
goto end

:rebuild
echo Clean rebuilding development environment...
call :stop
call :clean
echo Building and starting containers...
docker-compose -f docker-compose.dev.yml up --build -d
echo.
echo Waiting for services to be ready...
timeout /t 15 >nul
echo.
echo Running database migrations...
docker-compose -f docker-compose.dev.yml exec api prisma migrate dev --name init
echo.
echo Rebuild complete!
echo API: http://localhost:8000
goto end

:seed
echo Running database seeding...
docker-compose -f docker-compose.dev.yml exec api python scripts/smart_seed.py
goto end

:reset_seed
echo Resetting seeding flag...
docker-compose -f docker-compose.dev.yml exec api python scripts/reset_seed_flag.py
echo Flag reset! Database will be seeded on next deployment.
goto end

:end
endlocal
