# SOPA Backend - Script de Despliegue Automatizado
# Este script automatiza el proceso de despliegue descrito en DEPLOYMENT_GUIDE.md

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [switch]$Clean = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Seed = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Reset = $false
)

Write-Host "🚀 SOPA Backend - Script de Despliegue" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Entorno: $Environment" -ForegroundColor Yellow
Write-Host ""

# Función para verificar prerrequisitos
function Test-Prerequisites {
    Write-Host "🔍 Verificando prerrequisitos..." -ForegroundColor Blue
    
    # Verificar Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker encontrado: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: Docker no está instalado o no se puede ejecutar" -ForegroundColor Red
        Write-Host "   Por favor, instala Docker Desktop y asegúrate de que esté ejecutándose" -ForegroundColor Yellow
        exit 1
    }
    
    # Verificar Docker Compose
    try {
        $composeVersion = docker compose version
        Write-Host "✅ Docker Compose encontrado: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: Docker Compose no está disponible" -ForegroundColor Red
        exit 1
    }
    
    # Verificar archivos de configuración
    $configFile = if ($Environment -eq "dev") { ".env.dev" } else { ".env.prod" }
    if (-not (Test-Path $configFile)) {
        Write-Host "❌ Error: Archivo de configuración $configFile no encontrado" -ForegroundColor Red
        Write-Host "   Creando archivo desde ejemplo..." -ForegroundColor Yellow
        
        $exampleFile = "$configFile.example"
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $configFile
            Write-Host "✅ Archivo $configFile creado desde $exampleFile" -ForegroundColor Green
            Write-Host "   ⚠️  IMPORTANTE: Edita $configFile con tus configuraciones antes de continuar" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host "❌ Error: Tampoco se encontró $exampleFile" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ Archivo de configuración $configFile encontrado" -ForegroundColor Green
    }
    
    return $true
}

# Función para limpiar contenedores existentes
function Invoke-Cleanup {
    Write-Host "🧹 Limpiando contenedores existentes..." -ForegroundColor Blue
    
    $composeFile = "docker-compose.$Environment.yml"
    
    try {
        docker compose -f $composeFile down -v
        Write-Host "✅ Contenedores detenidos y volúmenes eliminados" -ForegroundColor Green
        
        if ($Clean) {
            Write-Host "🔄 Realizando limpieza completa del sistema Docker..." -ForegroundColor Blue
            docker system prune -f
            Write-Host "✅ Limpieza del sistema Docker completada" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Advertencia: Error al limpiar contenedores (puede ser que no existan)" -ForegroundColor Yellow
    }
}

# Función para construir e iniciar servicios
function Start-Services {
    Write-Host "🏗️  Construyendo e iniciando servicios..." -ForegroundColor Blue
    
    $composeFile = "docker-compose.$Environment.yml"
    
    try {
        # Construir e iniciar en modo detached
        docker compose -f $composeFile up --build -d
        
        Write-Host "✅ Servicios iniciados exitosamente" -ForegroundColor Green
        Write-Host ""
        
        # Mostrar estado de los contenedores
        Write-Host "📊 Estado de los contenedores:" -ForegroundColor Blue
        docker compose -f $composeFile ps
        
    } catch {
        Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
        Write-Host "Mostrando logs para diagnóstico..." -ForegroundColor Yellow
        docker compose -f $composeFile logs
        exit 1
    }
}

# Función para esperar que los servicios estén listos
function Wait-ForServices {
    Write-Host "⏳ Esperando que los servicios estén listos..." -ForegroundColor Blue
    
    $maxWait = 60
    $waited = 0
    $interval = 5
    
    while ($waited -lt $maxWait) {
        try {
            # Verificar PostgreSQL
            $pgReady = docker exec "sopa_postgres_$Environment" pg_isready -U postgres 2>$null
            if ($pgReady -match "accepting connections") {
                Write-Host "✅ PostgreSQL está listo" -ForegroundColor Green
                return $true
            }
        } catch {
            # Continuar esperando
        }
        
        Write-Host "   Esperando servicios... ($waited/$maxWait segundos)" -ForegroundColor Yellow
        Start-Sleep -Seconds $interval
        $waited += $interval
    }
    
    Write-Host "❌ Timeout esperando que los servicios estén listos" -ForegroundColor Red
    return $false
}

# Función para configurar base de datos
function Initialize-Database {
    Write-Host "🗄️  Configurando base de datos..." -ForegroundColor Blue
    
    $apiContainer = "sopa_api_$Environment"
    
    try {
        # Generar cliente de Prisma
        Write-Host "   Generando cliente de Prisma..." -ForegroundColor Yellow
        docker exec $apiContainer prisma generate
        
        # Ejecutar migraciones
        Write-Host "   Ejecutando migraciones..." -ForegroundColor Yellow
        docker exec $apiContainer prisma migrate deploy
        
        # Seed de la base de datos si se solicita
        if ($Seed -or $Reset) {
            Write-Host "   Poblando base de datos..." -ForegroundColor Yellow
            if ($Reset) {
                docker exec $apiContainer python scripts/db_manager.py reset-seed
            } else {
                docker exec $apiContainer python scripts/db_manager.py seed
            }
        }
        
        Write-Host "✅ Base de datos configurada exitosamente" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Error configurando base de datos" -ForegroundColor Red
        Write-Host "Mostrando logs del contenedor API..." -ForegroundColor Yellow
        docker logs $apiContainer
        exit 1
    }
}

# Función para verificar funcionamiento
function Test-Deployment {
    Write-Host "🔍 Verificando funcionamiento del API..." -ForegroundColor Blue
    
    $maxRetries = 10
    $retries = 0
    $delay = 3
    
    while ($retries -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ API respondiendo correctamente" -ForegroundColor Green
                Write-Host "   Código de estado: $($response.StatusCode)" -ForegroundColor Green
                return $true
            }
        } catch {
            $retries++
            if ($retries -lt $maxRetries) {
                Write-Host "   Intento $retries/$maxRetries fallido, reintentando en $delay segundos..." -ForegroundColor Yellow
                Start-Sleep -Seconds $delay
            }
        }
    }
    
    Write-Host "❌ El API no responde después de $maxRetries intentos" -ForegroundColor Red
    return $false
}

# Función para mostrar información post-despliegue
function Show-DeploymentInfo {
    Write-Host ""
    Write-Host "🎉 ¡Despliegue completado exitosamente!" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 URLs Disponibles:" -ForegroundColor Cyan
    Write-Host "   • API: http://localhost:8000" -ForegroundColor White
    Write-Host "   • Documentación: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "🐘 Base de Datos PostgreSQL:" -ForegroundColor Cyan
    Write-Host "   • Host: localhost:5432" -ForegroundColor White
    Write-Host "   • Database: sopa_$Environment" -ForegroundColor White
    Write-Host "   • Usuario: postgres" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Comandos Útiles:" -ForegroundColor Cyan
    Write-Host "   • Ver logs: docker compose -f docker-compose.$Environment.yml logs -f" -ForegroundColor White
    Write-Host "   • Parar servicios: docker compose -f docker-compose.$Environment.yml down" -ForegroundColor White
    Write-Host "   • Acceder API container: docker exec -it sopa_api_$Environment bash" -ForegroundColor White
    Write-Host ""
}

# Función principal
function Main {
    try {
        # Verificar prerrequisitos
        $prerequisitesOk = Test-Prerequisites
        if (-not $prerequisitesOk) {
            Write-Host "❌ Por favor, configura las variables de entorno y ejecuta nuevamente" -ForegroundColor Red
            exit 1
        }
        
        # Limpiar si se solicita
        if ($Clean -or $Reset) {
            Invoke-Cleanup
        }
        
        # Iniciar servicios
        Start-Services
        
        # Esperar que los servicios estén listos
        if (-not (Wait-ForServices)) {
            exit 1
        }
        
        # Configurar base de datos
        Initialize-Database
        
        # Verificar funcionamiento
        if (-not (Test-Deployment)) {
            Write-Host "⚠️  El API puede no estar completamente funcional" -ForegroundColor Yellow
        }
        
        # Mostrar información
        Show-DeploymentInfo
        
    } catch {
        Write-Host "❌ Error durante el despliegue: $_" -ForegroundColor Red
        exit 1
    }
}

# Ejecutar script principal
Main
