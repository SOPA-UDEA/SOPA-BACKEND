@echo off
echo Stopping production environment...

docker-compose -f docker-compose.prod.yml down

echo Production environment stopped!
