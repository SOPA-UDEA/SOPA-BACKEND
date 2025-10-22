@echo off
REM SOPA Backend - Script de Despliegue Simple para Windows
REM Este script proporciona una interfaz simple para desplegar el backend

title SOPA Backend - Deployment Manager

:menu
cls
echo.
echo ==========================================
echo    SOPA Backend - Deployment Manager
echo ==========================================
echo.
echo Selecciona una opcion:
echo.
echo 1. Despliegue completo - Desarrollo (Recomendado)
echo 2. Despliegue completo - Produccion
echo 3. Iniciar servicios existentes - Desarrollo
echo 4. Iniciar servicios existentes - Produccion
echo 5. Parar todos los servicios
echo 6. Limpiar y rebuild completo - Desarrollo
echo 7. Ver logs en tiempo real
echo 8. Verificar estado de servicios
echo 9. Acceder al contenedor de la API
echo 0. Salir
echo.
set /p choice="Ingresa tu opcion (0-9): "

if "%choice%"=="1" goto deploy_dev_full
if "%choice%"=="2" goto deploy_prod_full
if "%choice%"=="3" goto start_dev
if "%choice%"=="4" goto start_prod
if "%choice%"=="5" goto stop_all
if "%choice%"=="6" goto clean_rebuild_dev
if "%choice%"=="7" goto show_logs
if "%choice%"=="8" goto check_status
if "%choice%"=="9" goto access_container
if "%choice%"=="0" goto exit

echo Opcion invalida. Presiona cualquier tecla para continuar...
pause >nul
goto menu

:deploy_dev_full
cls
echo.
echo ==========================================
echo   Despliegue Completo - Desarrollo
echo ==========================================
echo.
echo Este proceso hara:
echo 1. Verificar prerrequisitos
echo 2. Construir imagenes Docker
echo 3. Iniciar servicios (PostgreSQL, Redis, API)
echo 4. Configurar base de datos
echo 5. Poblar datos iniciales
echo.
echo Presiona cualquier tecla para continuar o Ctrl+C para cancelar...
pause >nul

echo Iniciando despliegue de desarrollo...
powershell -ExecutionPolicy Bypass -File deploy.ps1 -Environment dev -Seed
pause
goto menu

:deploy_prod_full
cls
echo.
echo ==========================================
echo   Despliegue Completo - Produccion
echo ==========================================
echo.
echo ADVERTENCIA: Este es un despliegue de produccion
echo Asegurate de tener configurado correctamente .env.prod
echo.
echo Presiona cualquier tecla para continuar o Ctrl+C para cancelar...
pause >nul

echo Iniciando despliegue de produccion...
powershell -ExecutionPolicy Bypass -File deploy.ps1 -Environment prod -Seed
pause
goto menu

:start_dev
cls
echo Iniciando servicios de desarrollo...
docker compose -f docker-compose.dev.yml up -d
echo.
echo Servicios iniciados. Verificando estado...
docker compose -f docker-compose.dev.yml ps
pause
goto menu

:start_prod
cls
echo Iniciando servicios de produccion...
docker compose -f docker-compose.prod.yml up -d
echo.
echo Servicios iniciados. Verificando estado...
docker compose -f docker-compose.prod.yml ps
pause
goto menu

:stop_all
cls
echo Deteniendo todos los servicios...
echo.
echo Parando desarrollo...
docker compose -f docker-compose.dev.yml down 2>nul
echo Parando produccion...
docker compose -f docker-compose.prod.yml down 2>nul
echo.
echo Todos los servicios han sido detenidos.
pause
goto menu

:clean_rebuild_dev
cls
echo.
echo ==========================================
echo   Limpiar y Rebuild Completo
echo ==========================================
echo.
echo ADVERTENCIA: Esto eliminara todos los datos locales
echo Esta accion no se puede deshacer.
echo.
echo Presiona cualquier tecla para continuar o Ctrl+C para cancelar...
pause >nul

echo Ejecutando limpieza y rebuild completo...
powershell -ExecutionPolicy Bypass -File deploy.ps1 -Environment dev -Clean -Reset
pause
goto menu

:show_logs
cls
echo.
echo Selecciona que logs ver:
echo.
echo 1. Todos los servicios (desarrollo)
echo 2. Solo API (desarrollo)
echo 3. Solo Base de datos (desarrollo)
echo 4. Todos los servicios (produccion)
echo 5. Volver al menu principal
echo.
set /p log_choice="Selecciona opcion (1-5): "

if "%log_choice%"=="1" (
    cls
    echo Mostrando logs de todos los servicios [desarrollo] - Presiona Ctrl+C para salir
    docker compose -f docker-compose.dev.yml logs -f
    goto menu
)
if "%log_choice%"=="2" (
    cls
    echo Mostrando logs de la API [desarrollo] - Presiona Ctrl+C para salir
    docker logs -f sopa_api_dev
    goto menu
)
if "%log_choice%"=="3" (
    cls
    echo Mostrando logs de PostgreSQL [desarrollo] - Presiona Ctrl+C para salir
    docker logs -f sopa_postgres_dev
    goto menu
)
if "%log_choice%"=="4" (
    cls
    echo Mostrando logs de todos los servicios [produccion] - Presiona Ctrl+C para salir
    docker compose -f docker-compose.prod.yml logs -f
    goto menu
)
if "%log_choice%"=="5" goto menu

echo Opcion invalida.
pause
goto show_logs

:check_status
cls
echo.
echo ==========================================
echo      Estado de los Servicios
echo ==========================================
echo.
echo === Desarrollo ===
docker compose -f docker-compose.dev.yml ps 2>nul
echo.
echo === Produccion ===
docker compose -f docker-compose.prod.yml ps 2>nul
echo.
echo === Health Check ===
echo Verificando API...
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL%==0 (
    echo ✅ API respondiendo correctamente
) else (
    echo ❌ API no responde o no esta disponible
)
echo.
echo === URLs Disponibles ===
echo • API: http://localhost:8000
echo • Documentacion: http://localhost:8000/docs
echo • Health Check: http://localhost:8000/health
echo.
pause
goto menu

:access_container
cls
echo.
echo Selecciona el contenedor al que deseas acceder:
echo.
echo 1. API (desarrollo)
echo 2. PostgreSQL (desarrollo)
echo 3. API (produccion)
echo 4. PostgreSQL (produccion)
echo 5. Volver al menu
echo.
set /p container_choice="Selecciona opcion (1-5): "

if "%container_choice%"=="1" (
    cls
    echo Accediendo al contenedor de la API [desarrollo]...
    echo Escribe 'exit' para salir del contenedor.
    echo.
    docker exec -it sopa_api_dev bash
    goto menu
)
if "%container_choice%"=="2" (
    cls
    echo Accediendo al contenedor de PostgreSQL [desarrollo]...
    echo Escribe '\q' para salir de psql.
    echo.
    docker exec -it sopa_postgres_dev psql -U postgres -d sopa_dev
    goto menu
)
if "%container_choice%"=="3" (
    cls
    echo Accediendo al contenedor de la API [produccion]...
    echo Escribe 'exit' para salir del contenedor.
    echo.
    docker exec -it sopa_api_prod bash
    goto menu
)
if "%container_choice%"=="4" (
    cls
    echo Accediendo al contenedor de PostgreSQL [produccion]...
    echo Escribe '\q' para salir de psql.
    echo.
    docker exec -it sopa_postgres_prod psql -U postgres -d sopa_prod
    goto menu
)
if "%container_choice%"=="5" goto menu

echo Opcion invalida.
pause
goto access_container

:exit
cls
echo.
echo Gracias por usar SOPA Backend Deployment Manager!
echo.
exit
