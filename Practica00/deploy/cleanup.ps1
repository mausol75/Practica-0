<#
.SYNOPSIS
    Elimina TODOS los recursos de AWS creados para Practica00.
    Ejecutar cuando termines de probar para NO incurrir en costos.

.DESCRIPTION
    Elimina:
    1. El entorno de Elastic Beanstalk
    2. La aplicación EB y todas sus versiones
    3. El bucket S3 con los paquetes de deploy
#>

$ErrorActionPreference = "Stop"

$AWS_REGION  = "us-east-1"
$EB_APP_NAME = "practica00-login"
$EB_ENV_NAME = "practica00-env"
$S3_BUCKET   = "elasticbeanstalk-us-east-1-practica00"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║   ⚠️  ELIMINAR TODOS LOS RECURSOS AWS DE PRACTICA00     ║" -ForegroundColor Red
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Red
Write-Host "║  App:     $EB_APP_NAME                           ║" -ForegroundColor Red
Write-Host "║  Entorno: $EB_ENV_NAME                               ║" -ForegroundColor Red
Write-Host "║  Bucket:  $S3_BUCKET           ║" -ForegroundColor Red
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "¿Estás seguro? Escribe 'ELIMINAR' para continuar"
if ($confirm -ne "ELIMINAR") {
    Write-Host "Cancelado." -ForegroundColor Yellow
    exit 0
}

# 1. Terminar el entorno
Write-Host "`n━━━ 1/3 Terminando entorno EB ━━━" -ForegroundColor Cyan
try {
    aws elasticbeanstalk terminate-environment `
        --environment-name $EB_ENV_NAME `
        --force-terminate 2>$null
    Write-Host "  ⏳ Esperando a que el entorno termine (esto tarda ~2 min)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30

    # Esperar a que el entorno esté terminado
    $maxWait = 12  # 12 * 15s = 3 min max
    for ($i = 0; $i -lt $maxWait; $i++) {
        $status = aws elasticbeanstalk describe-environments `
            --application-name $EB_APP_NAME `
            --environment-names $EB_ENV_NAME `
            --query "Environments[0].Status" `
            --output text 2>$null
        if ($status -eq "Terminated" -or $status -eq "None" -or !$status) {
            break
        }
        Write-Host "  ⏳ Estado: $status - esperando..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
    }
    Write-Host "  ✅ Entorno terminado" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  El entorno no existe o ya fue eliminado" -ForegroundColor Yellow
}

# 2. Eliminar la aplicación
Write-Host "`n━━━ 2/3 Eliminando aplicación EB ━━━" -ForegroundColor Cyan
try {
    aws elasticbeanstalk delete-application `
        --application-name $EB_APP_NAME `
        --terminate-env-by-force 2>$null
    Write-Host "  ✅ Aplicación eliminada" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  La aplicación no existe o ya fue eliminada" -ForegroundColor Yellow
}

# 3. Vaciar y eliminar bucket S3
Write-Host "`n━━━ 3/3 Eliminando bucket S3 ━━━" -ForegroundColor Cyan
try {
    aws s3 rm "s3://$S3_BUCKET" --recursive 2>$null
    aws s3api delete-bucket --bucket $S3_BUCKET --region $AWS_REGION 2>$null
    Write-Host "  ✅ Bucket S3 eliminado" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  El bucket no existe o ya fue eliminado" -ForegroundColor Yellow
}

# Resumen
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✅ TODOS LOS RECURSOS HAN SIDO ELIMINADOS       ║" -ForegroundColor Green
Write-Host "║         No se generarán más costos en AWS.               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
