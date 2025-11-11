from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime
import uuid
from botocore.config import Config

app = FastAPI(title="Taller EC2 API", version="1.0.0")

# Configuración de S3
S3_BUCKET_NAME = "vrtxdb566"  # Cambiar por tu bucket
session = boto3.Session()
s3_client = session.client('s3', config=Config(signature_version='s3v4'))


# Modelo de validación con Pydantic
class Persona(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la persona")
    edad: int = Field(..., gt=0, lt=150, description="Edad de la persona")
    email: str = Field(..., description="Email de la persona")
    telefono: str = Field(..., min_length=7, max_length=15, description="Teléfono de la persona")
    ciudad: str = Field(..., min_length=1, max_length=100, description="Ciudad de residencia")
    
    @field_validator('email')
    def validar_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Email debe tener formato válido')
        return v
    
    @field_validator('telefono')
    def validar_telefono(cls, v):
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Teléfono debe contener solo números, espacios, + o -')
        return v

@app.get("/")
def root():
    """Endpoint raíz para verificar que el servicio está funcionando"""
    return {
        "mensaje": "API Taller EC2 funcionando correctamente",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/insert")
async def insert(persona: Persona):
    """
    Endpoint POST que recibe datos de una persona, los valida,
    los almacena en S3 y retorna la cantidad total de archivos en el bucket.
    """
    try:
        # Generar nombre único para el archivo
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"persona_{timestamp}_{file_id}.json"
        
        # Convertir el objeto Persona a diccionario y agregar metadata
        persona_data = persona.model_dump()
        persona_data['id'] = file_id
        persona_data['fecha_registro'] = datetime.now().isoformat()
        
        # Convertir a JSON
        json_data = json.dumps(persona_data, indent=2, ensure_ascii=False)
        
        # Subir archivo a S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=json_data,
            ContentType='application/json'
        )
        
        # Contar archivos en el bucket
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        cantidad_archivos = response.get('KeyCount', 0)
        
        return {
            "mensaje": "Persona registrada exitosamente",
            "archivo": file_name,
            "cantidad_archivos_total": cantidad_archivos,
            "datos_guardados": persona_data
        }
        
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar en S3: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/count")
def count_files():
    """Endpoint para consultar la cantidad de archivos en el bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        cantidad = response.get('KeyCount', 0)
        return {
            "cantidad_archivos": cantidad,
            "bucket": S3_BUCKET_NAME
        }
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar S3: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "service": "running"}