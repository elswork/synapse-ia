FROM python:3.10-slim

# Evitar que Python genere archivos .pyc y use el buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements antes para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del repositorio
COPY . .

# Comando por defecto (interactivo para entrar al contenedor)
CMD ["python3", "tools/athena_brain.py"]
