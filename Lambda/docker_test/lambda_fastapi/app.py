from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Ejemplo sencillo FastAPI + Mangum")

@app.get("/")
async def read_root():
    return {"mensaje": "Hola desde FastAPI en AWS Lambda"}

@app.get("/saludo/{nombre}")
async def saludar(nombre: str):
    return {"saludo": f"Hola, {nombre}. Bienvenido a la API!"}

handler = Mangum(app)
