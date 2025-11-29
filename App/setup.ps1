# Setup Script: Descarga las librerías JAR necesarias para el proyecto

Write-Host "=== SETUP: Descargando dependencias ===" -ForegroundColor Cyan

# Crear carpeta libs si no existe
$libsDir = "libs"
if (-not (Test-Path $libsDir)) {
    New-Item -ItemType Directory -Path $libsDir | Out-Null
    Write-Host "Carpeta libs/ creada" -ForegroundColor Green
}

# Definir dependencias
$dependencies = @{
    "sqlite-jdbc-3.44.0.0.jar" = "https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.44.0.0/sqlite-jdbc-3.44.0.0.jar"
    "slf4j-api-2.0.9.jar" = "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar"
    "slf4j-nop-2.0.9.jar" = "https://repo1.maven.org/maven2/org/slf4j/slf4j-nop/2.0.9/slf4j-nop-2.0.9.jar"
}

# Descargar cada dependencia
foreach ($jar in $dependencies.Keys) {
    $destino = Join-Path $libsDir $jar
    
    if (Test-Path $destino) {
        Write-Host "Ya existe: $jar" -ForegroundColor Yellow
    } else {
        Write-Host "Descargando: $jar" -ForegroundColor White
        try {
            Invoke-WebRequest -Uri $dependencies[$jar] -OutFile $destino -UseBasicParsing
            Write-Host "Descargado: $jar" -ForegroundColor Green
        } catch {
            Write-Host "ERROR descargando $jar : $_" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== SETUP COMPLETADO ===" -ForegroundColor Cyan
Write-Host "Librerias descargadas en: $libsDir/" -ForegroundColor Green
Write-Host "`nSiguientes pasos:" -ForegroundColor Yellow
Write-Host "  1. Ejecuta: .\compile.ps1" -ForegroundColor White
Write-Host "  2. Ejecuta: .\run.ps1" -ForegroundColor White
