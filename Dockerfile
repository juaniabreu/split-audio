FROM python:3.10-slim

# Instalar ffmpeg y otras dependencias
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir Flask

# Copiar archivos
WORKDIR /app
COPY . /app

# Exponer puerto
EXPOSE 10000

# Iniciar servidor
CMD ["python", "app.py"]
