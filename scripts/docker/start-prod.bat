@echo off
echo Starting production environment...

if not exist .env.prod (
    echo Error: .env.prod file not found!
    echo Please copy .env.prod.example to .env.prod and configure it.
    pause
    exit /b 1
)

echo Starting containers...
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

echo Production environment started!
echo API: http://localhost:%API_PORT%

pause
