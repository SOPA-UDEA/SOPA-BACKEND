@echo off
echo Starting development environment...

echo Starting containers...
docker-compose -f docker-compose.dev.yml up -d

echo Development environment started!
echo API: http://localhost:8000
echo Database: localhost:5432
echo Redis: localhost:6379

pause
