@echo off
title SOPA Backend - Configuracion Inicial

echo.
echo =========================================
echo   SOPA Backend - Configuracion Inicial
echo =========================================
echo.
echo Este script te ayudara a configurar tu entorno para ejecutar el backend de SOPA.
echo.

REM Verificar si Docker esta instalado
echo [1/4] Verificando Docker Desktop...
docker --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo ✅ Docker Desktop encontrado y funcionando
    goto check_compose
) else (
    echo ❌ Docker Desktop no esta disponible
    echo.
    echo SOLUCION:
    echo 1. Si acabas de instalar Docker, reinicia tu computadora
    echo 2. Si no has instalado Docker, ejecuta: winget install Docker.DockerDesktop
    echo 3. Asegurate de que Docker Desktop este ejecutandose
    echo.
    echo Presiona cualquier tecla para intentar abrir Docker Desktop...
    pause >nul
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
    if %ERRORLEVEL%==0 (
        echo Docker Desktop iniciando... Espera unos minutos y ejecuta este script nuevamente.
    ) else (
        echo No se pudo iniciar Docker Desktop automaticamente.
        echo Por favor, inicialo manualmente desde el menu de Windows.
    )
    echo.
    pause
    exit /b 1
)

:check_compose
echo [2/4] Verificando Docker Compose...
docker compose version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo ✅ Docker Compose disponible
) else (
    echo ❌ Docker Compose no disponible
    echo Esto es extraño, Docker Desktop deberia incluirlo...
    pause
    exit /b 1
)

echo [3/4] Verificando archivos de configuracion...
if exist ".env.dev" (
    echo ✅ Archivo .env.dev encontrado
) else (
    if exist ".env.dev.example" (
        echo ⚠️  Creando .env.dev desde ejemplo...
        copy ".env.dev.example" ".env.dev" >nul
        echo ✅ Archivo .env.dev creado
    ) else (
        echo ❌ No se encontro archivo de configuracion
        pause
        exit /b 1
    )
)

echo [4/4] Verificando archivos Docker...
if exist "docker-compose.dev.yml" (
    echo ✅ docker-compose.dev.yml encontrado
) else (
    echo ❌ docker-compose.dev.yml no encontrado
    pause
    exit /b 1
)

if exist "Dockerfile" (
    echo ✅ Dockerfile encontrado
) else (
    echo ❌ Dockerfile no encontrado
    pause
    exit /b 1
)

echo.
echo =========================================
echo        ✅ Configuracion Completa
echo =========================================
echo.
echo Tu entorno esta listo para ejecutar SOPA Backend!
echo.
echo Opciones disponibles:
echo.
echo 1. Iniciar despliegue automatico (Recomendado)
echo 2. Usar el administrador de despliegue
echo 3. Despliegue manual con PowerShell
echo 4. Salir
echo.
set /p choice="Selecciona una opcion (1-4): "

if "%choice%"=="1" goto auto_deploy
if "%choice%"=="2" goto deploy_manager
if "%choice%"=="3" goto manual_deploy
if "%choice%"=="4" goto end

echo Opcion invalida.
pause
goto end

:auto_deploy
echo.
echo Iniciando despliegue automatico...
echo Esto construira e iniciara todos los servicios con datos de prueba.
echo.
echo Presiona Ctrl+C si deseas cancelar, o cualquier tecla para continuar...
pause >nul

REM Ejecutar despliegue completo
powershell -ExecutionPolicy Bypass -Command "& '.\deploy.ps1' -Environment dev -Seed"

echo.
echo Despliegue completado! Revisa los mensajes anteriores para verificar el estado.
pause
goto end

:deploy_manager
echo.
echo Abriendo administrador de despliegue...
deploy-manager.bat
goto end

:manual_deploy
echo.
echo Para despliegue manual, puedes usar estos comandos:
echo.
echo # Despliegue completo con datos:
echo powershell -ExecutionPolicy Bypass -File deploy.ps1 -Environment dev -Seed
echo.
echo # Despliegue limpio (borra datos existentes):
echo powershell -ExecutionPolicy Bypass -File deploy.ps1 -Environment dev -Clean -Reset
echo.
echo # Solo construir e iniciar servicios:
echo docker compose -f docker-compose.dev.yml up --build -d
echo.
pause
goto end

:end
echo.
echo Gracias por usar SOPA Backend!
echo.
echo Si tienes problemas:
echo 1. Revisa QUICK_START.md para inicio rapido
echo 2. Consulta DEPLOYMENT_GUIDE.md para la guia completa
echo 3. Usa deploy-manager.bat para una interfaz grafica
echo.
pause
