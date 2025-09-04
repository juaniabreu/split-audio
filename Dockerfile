FROM python:3.10-slim

# Instalar ffmpeg y Flask
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir Flask

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todos los archivos del proyecto
COPY . /app

# Exponer el puerto usado por Flask (Render lo necesita)
EXPOSE 10000

# Ejecutar la aplicación
CMD ["python", "app.py"]
