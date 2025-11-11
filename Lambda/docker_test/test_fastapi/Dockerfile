# Imagen base ligera con Python preinstalado
FROM python:3.11-slim

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto al directorio /app del contenedor
COPY . /app

# Instalar las dependencias
RUN pip install -r requirements.txt

# Expone el puerto 8000 (para que se pueda acceder desde el navegador)
EXPOSE 8000

# Comando que se ejecutará cuando se inicie el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
