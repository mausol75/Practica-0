<#
.SYNOPSIS
    Termina la instancia EC2 de Practica00 para dejar de pagar.

.DESCRIPTION
    Busca la instancia por nombre 'practica00-server' y la termina.
    Opcionalmente libera la Elastic IP asociada.
#>

$ErrorActionPreference = "Stop"
$AWS_REGION = "us-east-1"
$INSTANCE_NAME = "practica00-server"

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Red
Write-Host "   ELIMINAR INSTANCIA EC2: $INSTANCE_NAME" -ForegroundColor Red
Write-Host "===========================================================" -ForegroundColor Red
Write-Host ""

# Buscar instancia
Write-Host "Buscando instancia '$INSTANCE_NAME'..." -ForegroundColor Cyan
$instanceId = aws ec2 describe-instances `
    --region $AWS_REGION `
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running,stopped" `
    --query "Reservations[].Instances[].InstanceId" `
    --output text 2>&1

if (-not $instanceId -or $instanceId -eq "None" -or $instanceId -eq "") {
    Write-Host "  No se encontro ninguna instancia con nombre '$INSTANCE_NAME'" -ForegroundColor Yellow
    Write-Host "  Puede que ya haya sido eliminada." -ForegroundColor Yellow
    exit 0
}

Write-Host "  Instancia encontrada: $instanceId" -ForegroundColor Green

$confirm = Read-Host "`nEscribe 'ELIMINAR' para terminar la instancia"
if ($confirm -ne "ELIMINAR") {
    Write-Host "Cancelado." -ForegroundColor Yellow
    exit 0
}

# Terminar instancia
Write-Host "`nTerminando instancia $instanceId..." -ForegroundColor Cyan
aws ec2 terminate-instances --region $AWS_REGION --instance-ids $instanceId | Out-Null
Write-Host "  [OK] Instancia terminada" -ForegroundColor Green

# Buscar y liberar Elastic IP
Write-Host "`nBuscando Elastic IPs asociadas..." -ForegroundColor Cyan
$allocations = aws ec2 describe-addresses `
    --region $AWS_REGION `
    --filters "Name=instance-id,Values=$instanceId" `
    --query "Addresses[].AllocationId" `
    --output text 2>&1

if ($allocations -and $allocations -ne "None" -and $allocations -ne "") {
    foreach ($alloc in $allocations.Split("`t")) {
        Write-Host "  Liberando Elastic IP: $alloc" -ForegroundColor Yellow
        aws ec2 release-address --region $AWS_REGION --allocation-id $alloc
        Write-Host "  [OK] Elastic IP liberada" -ForegroundColor Green
    }
} else {
    Write-Host "  No se encontraron Elastic IPs asociadas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "  INSTANCIA EC2 ELIMINADA                                  " -ForegroundColor Green
Write-Host "  No se generaran mas costos por esta instancia.           " -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  RECUERDA: Desregistrar el runner en GitHub:" -ForegroundColor Yellow
Write-Host "  https://github.com/mausol75/Practica-0/settings/actions/runners" -ForegroundColor Yellow
