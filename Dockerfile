# Imagen base estable, optimizada y compatible con MediaPipe
FROM python:3.11-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias para MediaPipe + OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Directorio principal del proyecto
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar librerías Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo el código fuente
COPY src/ /app/src/

# Puerto para el servidor
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
