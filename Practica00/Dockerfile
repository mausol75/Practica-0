FROM python:3.12-slim

WORKDIR /app

# Copiar requirements y instalar dependencias primero (cache de Docker)
COPY sistema/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el sistema (backend + frontend)
COPY sistema/ ./sistema/

WORKDIR /app/sistema/backend

# Puerto de la app
EXPOSE 5000

# Arrancar la app
CMD ["python", "app.py"]
