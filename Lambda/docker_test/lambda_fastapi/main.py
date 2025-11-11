from mangum import Mangum
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()
handler=Mangum(app)

class Persona(BaseModel):
    nombre: str
    edad: int
    altura: float

@app.post("/persona")
async def obtener_persona(persona: Persona):
    print(persona.nombre, persona.edad, persona.altura)
    return persona

@app.get("/prueba")
async def obtener_variable(variable:str):
    return {"mensaje":f"{variable}"}

@app.get("/")
async def root():
    return {"mensaje":"Universidad EIA"}

# docker build --platform linux/amd64 --provenance=false -t test_so:latest .