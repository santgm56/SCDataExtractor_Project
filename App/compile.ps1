# Compile Script: Compila todos los archivos Java con las dependencias

Write-Host "=== COMPILANDO PROYECTO ===" -ForegroundColor Cyan

# Verificar que exista la carpeta libs
if (-not (Test-Path "libs")) {
    Write-Host "ERROR: Carpeta libs/ no encontrada" -ForegroundColor Red
    Write-Host "Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Crear carpeta bin si no existe
if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
    Write-Host "Carpeta bin/ creada" -ForegroundColor Green
}

# Construir classpath con todas las librerías
$classpath = "libs\*"

# Obtener todos los archivos .java
$srcFiles = Get-ChildItem -Path "src" -Filter "*.java" | ForEach-Object { $_.FullName }

Write-Host "Compilando archivos Java..." -ForegroundColor White

# Compilar
try {
    javac -cp $classpath -d "bin" $srcFiles
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== COMPILACION EXITOSA ===" -ForegroundColor Green
        Write-Host "Archivos compilados en: bin/" -ForegroundColor Green
        Write-Host "`nPara ejecutar: .\run.ps1" -ForegroundColor Yellow
    } else {
        Write-Host "`nERROR EN COMPILACION" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
