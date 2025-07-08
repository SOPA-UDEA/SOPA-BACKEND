@echo off
echo Cleaning and rebuilding Docker containers...

echo Stopping and removing containers...
docker-compose -f docker-compose.dev.yml down --remove-orphans

echo Removing unused Docker resources...
docker system prune -f

echo Building and starting containers...
docker-compose -f docker-compose.dev.yml up --build -d

echo Waiting for database to be ready...
timeout /t 10

echo Running database migrations...
docker-compose -f docker-compose.dev.yml exec api prisma migrate dev --name init

echo Setup complete! API should be available at http://localhost:8000
echo Database should be available at localhost:5432

pause
