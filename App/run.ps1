# Run Script: Ejecuta la aplicación con todas las dependencias

Write-Host "=== EJECUTANDO APP ===" -ForegroundColor Cyan

# Verificar que existan las carpetas necesarias
if (-not (Test-Path "bin")) {
    Write-Host "ERROR: Carpeta bin/ no encontrada" -ForegroundColor Red
    Write-Host "Ejecuta primero: .\compile.ps1" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "libs")) {
    Write-Host "ERROR: Carpeta libs/ no encontrada" -ForegroundColor Red
    Write-Host "Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Construir classpath: bin + todas las librerías
$classpath = "bin;libs\*"

Write-Host "Iniciando aplicacion...`n" -ForegroundColor Green

# Ejecutar
try {
    java -cp $classpath App
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== EJECUCION COMPLETADA ===" -ForegroundColor Green
    } else {
        Write-Host "`nERROR EN EJECUCION (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
