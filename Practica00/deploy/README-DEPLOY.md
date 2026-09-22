# 🚀 Guía de Despliegue — Practica00 en AWS Elastic Beanstalk

Despliegue automático de la aplicación Flask de login en AWS usando Docker + GitHub Actions.

---

## Arquitectura del despliegue

```
┌──────────────┐     git push      ┌──────────────────┐
│  Tu máquina  │ ────────────────► │     GitHub        │
│  (código)    │                   │  (repositorio)    │
└──────────────┘                   └────────┬─────────┘
                                            │ GitHub Actions
                                            ↓
                                   ┌──────────────────┐
                                   │   Empaqueta ZIP   │
                                   │   Sube a S3       │
                                   └────────┬─────────┘
                                            ↓
                                   ┌──────────────────┐
                                   │  AWS Elastic      │
                                   │  Beanstalk        │
                                   │  (Docker)         │
                                   └────────┬─────────┘
                                            ↓
                                   ┌──────────────────┐
                                   │  App disponible   │
                                   │  en URL pública   │
                                   └──────────────────┘
```

---

## Prerrequisitos

| Herramienta | Verificar con | Instalar desde |
|-------------|--------------|----------------|
| AWS CLI     | `aws --version` | https://aws.amazon.com/cli/ |
| Git         | `git --version` | https://git-scm.com/ |
| Docker (opcional, para test local) | `docker --version` | https://www.docker.com/ |

Además necesitas:
- **Cuenta de AWS** con credenciales configuradas (`aws configure`).
- **Repositorio en GitHub** (ya lo tienes: `mausol75/Practica-0`).

---

## Paso 1: Setup inicial (UNA SOLA VEZ)

Ejecuta el script de setup desde la raíz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File Practica00\deploy\setup-inicial.ps1
```

Este script crea automáticamente:
- ✅ Bucket S3 para los paquetes de deploy.
- ✅ Aplicación en Elastic Beanstalk.
- ✅ Entorno Docker con instancia `t3.micro` (capa gratuita).
- ✅ Variable `SESSION_SECRET` configurada de forma segura.

---

## Paso 2: Configurar GitHub Secrets

Ve a tu repositorio en GitHub:

1. **Settings** → **Secrets and variables** → **Actions**
2. Click en **New repository secret**
3. Agrega estos dos secrets:

| Nombre del Secret | Valor |
|-------------------|-------|
| `AWS_ACCESS_KEY_ID` | Tu Access Key de AWS (la obtienes de `aws configure` o de la consola IAM) |
| `AWS_SECRET_ACCESS_KEY` | Tu Secret Key de AWS |

### ¿Cómo obtener las credenciales?

```powershell
# Ver tus credenciales actuales
aws configure list
```

O desde la **Consola de AWS**:
1. Ve a **IAM** → **Users** → tu usuario.
2. **Security credentials** → **Create access key**.

---

## Paso 3: Hacer push (despliegue automático)

Una vez completados los pasos 1 y 2, cada push a `main` despliega automáticamente:

```powershell
git add .
git commit -m "feat: configurar despliegue AWS EB + GitHub Actions"
git push origin main
```

### Ver el progreso del deploy:
1. Ve a tu repositorio en GitHub.
2. Click en la pestaña **Actions**.
3. Verás el workflow ejecutándose con cada paso.

---

## Paso 4: Verificar el despliegue

### Desde la terminal:
```powershell
# Ver estado del entorno
aws elasticbeanstalk describe-environments `
    --application-name practica00-login `
    --environment-names practica00-env `
    --query "Environments[0].[Status,CNAME,Health]" `
    --output table

# Ver la URL de la app
aws elasticbeanstalk describe-environments `
    --application-name practica00-login `
    --environment-names practica00-env `
    --query "Environments[0].CNAME" `
    --output text
```

### Desde el navegador:
Abre la URL que te da el comando anterior:
`http://practica00-env.xxxxx.us-east-1.elasticbeanstalk.com`

Prueba:
1. ✅ Login con `alumno` / `Practica123!`
2. ✅ Acceso al dashboard
3. ✅ Consulta de clima
4. ✅ Cerrar sesión

---

## 🛑 Paso 5: ELIMINAR el entorno (para no incurrir en costos)

> **⚠️ MUY IMPORTANTE:** Elastic Beanstalk usa instancias EC2 que generan costos.
> Cuando termines de probar, ELIMINA el entorno.

### Opción A — Eliminar solo el entorno (mantener la app):
```powershell
aws elasticbeanstalk terminate-environment `
    --environment-name practica00-env `
    --force-terminate
```

### Opción B — Eliminar TODO (app + entorno + versiones):
```powershell
# 1. Terminar el entorno
aws elasticbeanstalk terminate-environment `
    --environment-name practica00-env `
    --force-terminate

# 2. Esperar a que termine (1-2 minutos)
Write-Host "Esperando a que termine el entorno..."
Start-Sleep -Seconds 120

# 3. Eliminar la aplicación y todas sus versiones
aws elasticbeanstalk delete-application `
    --application-name practica00-login `
    --terminate-env-by-force

# 4. Vaciar y eliminar el bucket S3
aws s3 rm s3://elasticbeanstalk-us-east-1-practica00 --recursive
aws s3api delete-bucket --bucket elasticbeanstalk-us-east-1-practica00 --region us-east-1

Write-Host "✅ Todo eliminado. No se generarán más costos."
```

### Opción C — Script rápido de limpieza:
```powershell
powershell -ExecutionPolicy Bypass -File Practica00\deploy\cleanup.ps1
```

---

## Resumen de comandos útiles

| Acción | Comando |
|--------|---------|
| Ver estado | `aws elasticbeanstalk describe-environments --application-name practica00-login --environment-names practica00-env --query "Environments[0].Status" --output text` |
| Ver URL | `aws elasticbeanstalk describe-environments --application-name practica00-login --environment-names practica00-env --query "Environments[0].CNAME" --output text` |
| Ver logs | `aws elasticbeanstalk request-environment-info --environment-name practica00-env --info-type tail` |
| Reiniciar | `aws elasticbeanstalk restart-app-server --environment-name practica00-env` |
| **ELIMINAR** | `aws elasticbeanstalk terminate-environment --environment-name practica00-env --force-terminate` |

---

## Solución de problemas

### El workflow de GitHub falla
1. Revisa que los secrets `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` estén configurados.
2. Verifica que el nombre de la app y entorno coincidan con los del script de setup.

### La app no responde en la URL
1. Espera 3-5 minutos después del deploy (EB tarda en iniciar Docker).
2. Revisa los logs: `aws elasticbeanstalk request-environment-info --environment-name practica00-env --info-type tail`

### Health check falla
1. Verifica que el endpoint `/health` responda 200.
2. El puerto debe ser 8080 (configurado en el Dockerfile).
