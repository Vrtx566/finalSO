# Para instalar dependencias
# pip install fastapi uvicorn

# Para iniciar el servicio
# uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel): # BaseModel es una clase que nos va permitir validar el envío de datos por POST
    name: str = 'Mateo'
    description: str = 'Testing'
    price: float = 2000.35


# endpoint: el punto al cual yo quiero llamar de nuestra API
@app.get("/")
def read_root():
    return {"message": "Universidad EIA"}

@app.get("/items/{item_id}")
def read_item(item_id: int, query: str = None):
    return {"item_id": item_id, "query": query}

@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "description": item.description, "price": item.price}

