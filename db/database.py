import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("DATABASE_NAME")

if not MONGO_URI or not MONGO_DB:
    raise ValueError("Faltan MONGO_URL o DATABASE_NAME en el .env")

# Conectar al cliente de Mongo
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Colecciones
users_collection = db["users"]