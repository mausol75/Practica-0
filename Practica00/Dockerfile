FROM python:3.12-slim

WORKDIR /app

# Copiar requirements y instalar dependencias primero (cache de Docker)
COPY sistema/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el sistema (backend + frontend)
COPY sistema/ ./sistema/

WORKDIR /app/sistema/backend

# Health check para Elastic Beanstalk
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Puerto que Elastic Beanstalk espera
EXPOSE 8080

# Arrancar con gunicorn (servidor WSGI de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
