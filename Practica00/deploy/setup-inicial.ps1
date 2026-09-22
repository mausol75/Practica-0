<#
.SYNOPSIS
    Setup inicial de AWS Elastic Beanstalk para Practica00.
    Ejecutar UNA SOLA VEZ antes del primer deploy.

.DESCRIPTION
    Este script:
    1. Verifica que AWS CLI está instalado y configurado.
    2. Crea el bucket S3 para los deployments.
    3. Crea la aplicación en Elastic Beanstalk.
    4. Crea el entorno con Docker.
    5. Configura SESSION_SECRET como variable de entorno.

.NOTES
    Autor: Practica00 - Desarrollo de App para la Nube
    Requisitos: AWS CLI configurado con credenciales válidas
#>

$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────
# Configuración (AJUSTAR si es necesario)
# ─────────────────────────────────────────────────────────────
$AWS_REGION       = "us-east-1"
$EB_APP_NAME      = "practica00-login"
$EB_ENV_NAME      = "practica00-env"
$S3_BUCKET        = "elasticbeanstalk-us-east-1-practica00"
$INSTANCE_TYPE    = "t3.micro"
$PLATFORM         = "64bit Amazon Linux 2023 v4.4.4 running Docker"

# Generar SESSION_SECRET seguro
$SESSION_SECRET = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object { [char]$_ })

# ─────────────────────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────────────────────
function Write-Step($msg) {
    Write-Host "`n━━━ $msg ━━━" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "  ✅ $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "  ⚠️  $msg" -ForegroundColor Yellow
}

function Write-Err($msg) {
    Write-Host "  ❌ $msg" -ForegroundColor Red
}

# ─────────────────────────────────────────────────────────────
# 1. Verificar AWS CLI
# ─────────────────────────────────────────────────────────────
Write-Step "1/6 Verificando AWS CLI"

try {
    $awsVersion = aws --version 2>&1
    Write-Ok "AWS CLI encontrado: $awsVersion"
} catch {
    Write-Err "AWS CLI no está instalado. Instálalo desde: https://aws.amazon.com/cli/"
    exit 1
}

# Verificar credenciales
try {
    $identity = aws sts get-caller-identity --output json 2>&1 | ConvertFrom-Json
    Write-Ok "Cuenta AWS: $($identity.Account)"
    Write-Ok "Usuario:    $($identity.Arn)"
} catch {
    Write-Err "AWS CLI no tiene credenciales configuradas. Ejecuta: aws configure"
    exit 1
}

# ─────────────────────────────────────────────────────────────
# 2. Crear bucket S3
# ─────────────────────────────────────────────────────────────
Write-Step "2/6 Creando bucket S3: $S3_BUCKET"

$bucketExists = aws s3api head-bucket --bucket $S3_BUCKET 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Warn "El bucket ya existe, continuando..."
} else {
    if ($AWS_REGION -eq "us-east-1") {
        aws s3api create-bucket --bucket $S3_BUCKET --region $AWS_REGION
    } else {
        aws s3api create-bucket --bucket $S3_BUCKET --region $AWS_REGION `
            --create-bucket-configuration LocationConstraint=$AWS_REGION
    }
    Write-Ok "Bucket S3 creado exitosamente"
}

# ─────────────────────────────────────────────────────────────
# 3. Crear aplicación EB
# ─────────────────────────────────────────────────────────────
Write-Step "3/6 Creando aplicación Elastic Beanstalk: $EB_APP_NAME"

$appExists = aws elasticbeanstalk describe-applications `
    --application-names $EB_APP_NAME `
    --query "Applications[0].ApplicationName" `
    --output text 2>&1

if ($appExists -eq $EB_APP_NAME) {
    Write-Warn "La aplicación ya existe, continuando..."
} else {
    aws elasticbeanstalk create-application `
        --application-name $EB_APP_NAME `
        --description "Practica00 - Sistema de Login (Flask + Docker)"
    Write-Ok "Aplicación EB creada"
}

# ─────────────────────────────────────────────────────────────
# 4. Crear versión inicial (ZIP mínimo)
# ─────────────────────────────────────────────────────────────
Write-Step "4/6 Creando versión inicial"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
# Si estamos en deploy/, subir un nivel
if (-not (Test-Path "$projectRoot\Dockerfile")) {
    $projectRoot = Split-Path -Parent $projectRoot
}

Push-Location $projectRoot
try {
    # Crear ZIP del proyecto
    $zipPath = Join-Path $env:TEMP "practica00-initial.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath }

    Compress-Archive -Path @(
        "Dockerfile",
        ".dockerignore",
        ".ebextensions",
        "sistema"
    ) -DestinationPath $zipPath -Force

    # Subir a S3
    aws s3 cp $zipPath "s3://$S3_BUCKET/practica00-initial.zip"

    # Crear versión en EB
    aws elasticbeanstalk create-application-version `
        --application-name $EB_APP_NAME `
        --version-label "initial" `
        --source-bundle S3Bucket=$S3_BUCKET,S3Key="practica00-initial.zip" `
        --description "Version inicial"

    Write-Ok "Versión inicial creada y subida a S3"
} finally {
    Pop-Location
}

# ─────────────────────────────────────────────────────────────
# 5. Crear entorno EB
# ─────────────────────────────────────────────────────────────
Write-Step "5/6 Creando entorno: $EB_ENV_NAME (esto tarda ~5 minutos)"

$envExists = aws elasticbeanstalk describe-environments `
    --application-name $EB_APP_NAME `
    --environment-names $EB_ENV_NAME `
    --query "Environments[?Status!='Terminated'] | [0].EnvironmentName" `
    --output text 2>&1

if ($envExists -eq $EB_ENV_NAME) {
    Write-Warn "El entorno ya existe, continuando..."
} else {
    aws elasticbeanstalk create-environment `
        --application-name $EB_APP_NAME `
        --environment-name $EB_ENV_NAME `
        --solution-stack-name $PLATFORM `
        --version-label "initial" `
        --option-settings `
            "Namespace=aws:autoscaling:launchconfiguration,OptionName=InstanceType,Value=$INSTANCE_TYPE" `
            "Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=aws-elasticbeanstalk-ec2-role" `
            "Namespace=aws:elasticbeanstalk:environment:process:default,OptionName=HealthCheckPath,Value=/health" `
            "Namespace=aws:elasticbeanstalk:environment:process:default,OptionName=MatcherHTTPCode,Value=200"

    Write-Host "`n  ⏳ Esperando a que el entorno esté listo..." -ForegroundColor Yellow
    aws elasticbeanstalk wait environment-exists `
        --application-name $EB_APP_NAME `
        --environment-names $EB_ENV_NAME

    Write-Ok "Entorno creado"
}

# ─────────────────────────────────────────────────────────────
# 6. Configurar variables de entorno
# ─────────────────────────────────────────────────────────────
Write-Step "6/6 Configurando SESSION_SECRET en el entorno"

aws elasticbeanstalk update-environment `
    --application-name $EB_APP_NAME `
    --environment-name $EB_ENV_NAME `
    --option-settings "Namespace=aws:elasticbeanstalk:application:environment,OptionName=SESSION_SECRET,Value=$SESSION_SECRET"

Write-Ok "SESSION_SECRET configurado"

# ─────────────────────────────────────────────────────────────
# Resumen
# ─────────────────────────────────────────────────────────────
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ SETUP INICIAL COMPLETADO                    ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                             ║" -ForegroundColor Green
Write-Host "║  App:     $EB_APP_NAME                              ║" -ForegroundColor Green
Write-Host "║  Entorno: $EB_ENV_NAME                                  ║" -ForegroundColor Green
Write-Host "║  Región:  $AWS_REGION                                   ║" -ForegroundColor Green
Write-Host "║  Bucket:  $S3_BUCKET              ║" -ForegroundColor Green
Write-Host "║                                                             ║" -ForegroundColor Green
Write-Host "║  SIGUIENTE PASO:                                            ║" -ForegroundColor Yellow
Write-Host "║  Configura estos GitHub Secrets en tu repositorio:          ║" -ForegroundColor Yellow
Write-Host "║    - AWS_ACCESS_KEY_ID                                      ║" -ForegroundColor Yellow
Write-Host "║    - AWS_SECRET_ACCESS_KEY                                  ║" -ForegroundColor Yellow
Write-Host "║                                                             ║" -ForegroundColor Green
Write-Host "║  Luego haz: git add . && git commit && git push origin main ║" -ForegroundColor Green
Write-Host "║                                                             ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

# Obtener URL
$envUrl = aws elasticbeanstalk describe-environments `
    --application-name $EB_APP_NAME `
    --environment-names $EB_ENV_NAME `
    --query "Environments[0].CNAME" `
    --output text 2>&1

if ($envUrl -and $envUrl -ne "None") {
    Write-Host "`n  🌐 URL: http://$envUrl" -ForegroundColor Cyan
}
