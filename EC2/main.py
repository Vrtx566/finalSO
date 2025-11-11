from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from datetime import datetime
import io
import csv

app = FastAPI(title="FinalSO", version="1.0.0")

# Configuración de S3 (actualizar S3_BUCKET_NAME por el bucket real)
S3_BUCKET_NAME = "vrtxdb566"
PERSONAS_KEY = "personas.csv"

session = boto3.Session()
s3_client = session.client('s3', config=Config(signature_version='s3v4'))


class Persona(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la persona")
    edad: int = Field(..., ge=0, lt=150, description="Edad de la persona")
    altura: float = Field(..., gt=0, description="Altura en metros")


@app.get("/")
def root():
    return {"mensaje": "FinalSO funcionando correctamente", "timestamp": datetime.now().isoformat()}


def _read_csv_from_s3() -> list:
    """Lee el CSV desde S3 y devuelve una lista de filas (cada fila es dict).
    Si no existe el objeto, devuelve lista vacía.
    """
    try:
        resp = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=PERSONAS_KEY)
        body = resp['Body'].read().decode('utf-8')
        if not body.strip():
            return []
        f = io.StringIO(body)
        reader = csv.DictReader(f)
        return list(reader)
    except ClientError as e:
        err_code = e.response.get('Error', {}).get('Code')
        if err_code in ("NoSuchKey", "404"):
            return []
        raise


def _write_csv_to_s3(rows: list):
    """Escribe la lista de filas (dict) como CSV en S3 (sobrescribe el objeto)."""
    if not rows:
        # crear archivo vacío con cabecera
        fieldnames = ['nombre', 'edad', 'altura', 'fecha_registro']
    else:
        fieldnames = list(rows[0].keys())

    f = io.StringIO()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    csv_bytes = f.getvalue().encode('utf-8')
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=PERSONAS_KEY, Body=csv_bytes, ContentType='text/csv; charset=utf-8')


@app.post("/person")
async def add_person(persona: Persona):
    """Recibe nombre, edad y altura; valida con Pydantic y actualiza `personas.csv` en S3.
    El CSV es un solo recurso en el bucket y se sobrescribe/actualiza (append + upload).
    """
    try:
        # Leer contenido actual (si existe)
        rows = _read_csv_from_s3()

        # Preparar nueva fila
        nueva = {
            'nombre': persona.nombre,
            'edad': str(persona.edad),
            'altura': str(persona.altura),
            'fecha_registro': datetime.now().isoformat()
        }

        rows.append(nueva)

        # Escribir de nuevo el CSV en S3 (sobrescribe)
        _write_csv_to_s3(rows)

        return {"mensaje": "Persona añadida", "total_filas": len(rows)}

    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a S3: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


@app.get("/person/count")
def person_count():
    """Retorna el número de filas del CSV almacenado en S3 (excluye cabecera)."""
    try:
        rows = _read_csv_from_s3()
        return {"cantidad_filas": len(rows), "archivo": PERSONAS_KEY}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar S3: {e}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "running"}