#!/bin/bash

# Construir la imagen Docker usando el Dockerfile del directorio actual
docker build -t fastapi-test .

# Ejecutar el contenedor y mapear el puerto 8000 del contenedor al puerto 8000 del host
docker run -p 8000:8000 fastapi-test
