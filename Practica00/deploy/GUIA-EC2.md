# Guia de Despliegue -- Practica00 en EC2 con Runner Self-Hosted

## Datos del proyecto

| Dato | Valor |
|------|-------|
| Repositorio | `mausol75/Practica-0` |
| App | Flask + SQLite + Docker |
| Puerto publico | 80 (HTTP) |
| Runner label | `practica00-prod` |

---

## Paso 1: Crear la EC2

En la consola de AWS:

1. **Launch Instance**
   - Nombre: `practica00-server`
   - AMI: Ubuntu Server 24.04 LTS (x86_64)
   - Tipo: `t3.micro` (capa gratuita)
   - Key pair: crear o usar una existente (guardar el `.pem`)
   - Storage: 20 GiB gp3

2. **Security Group** (crear uno nuevo):

   | Puerto | Origen | Uso |
   |--------|--------|-----|
   | 22/TCP | Tu IP (`x.x.x.x/32`) | SSH |
   | 80/TCP | `0.0.0.0/0` y `::/0` | App HTTP |

3. **Elastic IP** (opcional pero recomendado):
   - EC2 > Elastic IPs > Allocate > Associate a la instancia

---

## Paso 2: Conectar por SSH

```bash
chmod 400 tu-clave.pem
ssh -i tu-clave.pem ubuntu@<IP_PUBLICA>
```

---

## Paso 3: Instalar Docker

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl git

# Instalar Docker (repositorio oficial)
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar
sudo docker version
sudo docker compose version
```

Crear swap (la t3.micro solo tiene 1 GiB de RAM):

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

---

## Paso 4: Crear usuario y directorios

```bash
sudo useradd --create-home --shell /bin/bash github-runner
sudo install -d -o github-runner -g github-runner -m 0750 /opt/actions-runner
sudo install -d -o root -g root -m 0755 /opt/practica00
sudo install -d -o root -g root -m 0700 /opt/practica00/shared
sudo install -d -o root -g root -m 0700 /opt/practica00/shared/.secrets
sudo install -d -o root -g root -m 0755 /opt/practica00/releases
```

NO ejecutar `usermod -aG docker github-runner`.

---

## Paso 5: Instalar y registrar el runner

### 5.1 Obtener token temporal

1. Ir a https://github.com/mausol75/Practica-0/settings/actions/runners
2. Click **New self-hosted runner**
3. Elegir **Linux** + **x64**
4. GitHub muestra los comandos de descarga y un token temporal

### 5.2 Descargar e instalar

```bash
sudo -iu github-runner
cd /opt/actions-runner

# COPIAR Y EJECUTAR los comandos de descarga que muestra GitHub
# (curl -o ... + tar xzf ...)
```

### 5.3 Registrar el runner

```bash
# Pegar el token cuando aparezca el prompt (no se muestra en pantalla)
read -rsp 'Token temporal de registro del runner: ' RUNNER_TOKEN
echo
./config.sh \
  --url https://github.com/mausol75/Practica-0 \
  --token "$RUNNER_TOKEN" \
  --name practica00-prod-ec2 \
  --labels practica00-prod \
  --work _work \
  --unattended \
  --replace
unset RUNNER_TOKEN
exit
```

### 5.4 Instalar como servicio

```bash
cd /opt/actions-runner
sudo ./svc.sh install github-runner
sudo ./svc.sh start
sudo ./svc.sh status
```

En GitHub el runner debe aparecer como **Idle** con labels `self-hosted`, `linux`, `x64`, `practica00-prod`.

---

## Paso 6: Crear secreto local

```bash
sudo sh -c 'umask 077; openssl rand -base64 48 > /opt/practica00/shared/.secrets/session_secret'
sudo chmod 600 /opt/practica00/shared/.secrets/session_secret
sudo chown root:root /opt/practica00/shared/.secrets/session_secret

# Verificar (NO imprimir el contenido)
sudo stat -c '%U:%G %a %s %n' /opt/practica00/shared/.secrets/*
```

---

## Paso 7: Crear script de despliegue

```bash
sudo tee /usr/local/sbin/deploy-practica00 >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail

BASE=/opt/practica00
SHARED="$BASE/shared"
RELEASES="$BASE/releases"
SOURCE=/opt/actions-runner/_work/Practica-0/Practica-0/Practica00
LOCK=/run/lock/practica00-deploy.lock

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

[[ $# -eq 1 ]] || die 'Uso: deploy-practica00 <sha-de-40-caracteres>'
sha=$1
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || die 'El SHA no es valido'
[[ "$(id -u)" -eq 0 ]] || die 'Este script debe ejecutarse como root'

exec 9>"$LOCK"
flock -n 9 || die 'Ya existe otro despliegue en curso'

for required in \
  "$SOURCE/compose.yaml" \
  "$SOURCE/compose.runner.yaml" \
  "$SOURCE/Dockerfile" \
  "$SHARED/.secrets/session_secret"; do
  [[ -e "$required" ]] || die "Falta $required"
done

release="$RELEASES/$sha"
previous=''
if [[ -L "$BASE/current" ]]; then
  previous=$(readlink -f "$BASE/current")
fi

install -d -o root -g root -m 0755 "$release"
rsync -a --delete \
  --exclude .git \
  --exclude node_modules \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  --exclude '*.pyc' \
  "$SOURCE/" "$release/"

# Enlazar secretos
ln -sfn "$SHARED/.secrets" "$release/.secrets"

compose() {
  RELEASE_SHA="$sha" docker compose \
    --project-directory "$release" \
    -f "$release/compose.yaml" \
    -f "$release/compose.runner.yaml" "$@"
}

rollback_on_error() {
  code=$?
  trap - ERR
  set +e
  printf 'El despliegue fallo con codigo %s.\n' "$code" >&2
  if [[ -n "$previous" && -d "$previous" ]]; then
    previous_sha=$(basename "$previous")
    printf 'Intentando restaurar contenedores de %s...\n' "$previous_sha" >&2
    RELEASE_SHA="$previous_sha" docker compose \
      --project-directory "$previous" \
      -f "$previous/compose.yaml" \
      -f "$previous/compose.runner.yaml" \
      up -d --no-build --remove-orphans
  fi
  exit "$code"
}
trap rollback_on_error ERR

compose config --quiet
compose build --pull app
compose up -d --no-build --remove-orphans

# Esperar health check
healthy=0
for _ in $(seq 1 60); do
  container_id=$(compose ps -q app)
  if [[ -n "$container_id" ]]; then
    state=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id")
    if [[ "$state" == "healthy" || "$state" == "running" ]]; then
      healthy=1
      break
    fi
  fi
  sleep 3
done
[[ "$healthy" == 1 ]] || die 'La app no llego a un estado saludable'

# Verificar endpoint /health
endpoint_ok=0
for _ in $(seq 1 30); do
  if curl --fail --silent --show-error http://localhost/health >/dev/null; then
    endpoint_ok=1
    break
  fi
  sleep 3
done
[[ "$endpoint_ok" == 1 ]] || die 'El endpoint /health no respondio'

# Actualizar symlink
ln -sfn "$release" "$BASE/current.next"
mv -Tf "$BASE/current.next" "$BASE/current"
docker image prune -f
trap - ERR
printf 'Despliegue completado: %s\n' "$sha"
SCRIPT
sudo chown root:root /usr/local/sbin/deploy-practica00
sudo chmod 0755 /usr/local/sbin/deploy-practica00
sudo bash -n /usr/local/sbin/deploy-practica00
```

---

## Paso 8: Permiso sudo minimo

```bash
sudo tee /etc/sudoers.d/practica00-github-runner >/dev/null <<'EOF'
github-runner ALL=(root) NOPASSWD: /usr/local/sbin/deploy-practica00 *
EOF
sudo chown root:root /etc/sudoers.d/practica00-github-runner
sudo chmod 0440 /etc/sudoers.d/practica00-github-runner
sudo visudo -cf /etc/sudoers.d/practica00-github-runner
```

Verificar:
```bash
sudo -u github-runner sudo -n -l
id github-runner
```

---

## Paso 9: Configurar GitHub

### 9.1 Entorno `production`

1. Ir a https://github.com/mausol75/Practica-0/settings/environments
2. **New environment** > Nombre: `production`
3. En **Deployment branches**: permitir solo `main`

### 9.2 Proteger `main` (opcional para practica)

Settings > Branches > Add rule para `main`:
- Require pull request reviews
- Require status checks (Validate)

---

## Paso 10: Primer despliegue

1. Hacer push de todos los cambios a `main`
2. Ir a **Actions** > **Validate and deploy production**
3. Click **Run workflow** > Branch `main`
4. Aprobar el entorno `production` si hay reviewer configurado

---

## Paso 11: Verificar

```bash
# En la EC2:
sudo docker compose \
  -f /opt/practica00/current/compose.yaml \
  -f /opt/practica00/current/compose.runner.yaml \
  --project-directory /opt/practica00/current \
  ps -a

# Health check
curl -fsS http://localhost/health

# Puertos (solo 22 y 80)
sudo ss -lntp
```

Desde tu navegador: `http://<IP_PUBLICA_EC2>`

---

## Paso 12: ELIMINAR TODO (para no pagar)

### Desde la consola de AWS:
1. **EC2 > Instances** > Seleccionar `practica00-server`
2. **Instance state > Terminate instance**
3. Si creaste Elastic IP: **EC2 > Elastic IPs > Release**

### O desde tu terminal (con AWS CLI):
```powershell
# Obtener el Instance ID
aws ec2 describe-instances --filters "Name=tag:Name,Values=practica00-server" --query "Reservations[].Instances[].InstanceId" --output text

# Terminar la instancia
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>
```

### Desregistrar el runner de GitHub:
1. Ir a https://github.com/mausol75/Practica-0/settings/actions/runners
2. Click en el runner > **Remove**

---

## Resumen de lo que NO se necesita configurar

| Credencial | Necesaria? |
|------------|-----------|
| AWS access keys en GitHub | NO |
| PAT de GitHub | NO |
| Clave SSH en GitHub | NO |
| GitHub Secrets | NO |
| ECR / S3 / Secrets Manager | NO |

Todo se maneja con el runner self-hosted y secretos locales en la EC2.
