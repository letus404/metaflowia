import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from routers.user_router import user_router, get_password_hash
from db.database import users_collection

# --- Configuración de FastAPI ---
app = FastAPI(
    title="User API",
    description="Gestión de usuarios (registro, login, invitado) con MongoDB",
    version="1.0.0",
)

# Contexto de PassLib para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Usuario por defecto en startup ---
async def create_default_user():
    # Si no existe el admin, lo crea
    existing = await users_collection.find_one({"username": "admin"})
    if not existing:
        hashed = get_password_hash("admin")
        await users_collection.insert_one({
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Administrador",
            "role": "admin",
            "disabled": False,
            "hashed_password": hashed,
        })


@app.on_event("startup")
async def on_startup():
    await create_default_user()


# --- CORS para que el front (por ej. http://localhost:3000) pueda hablar con este API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["*"] en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# NOTA: como tu frontend llama a /users/login, /users/register, etc.,
# aquí le ponemos el prefijo "/users" a todas las rutas.
app.include_router(user_router, prefix="/users", tags=["users"])


# --- Punto de entrada cuando ejecutás python backend/main.py directamente ---
if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))  # Usa el puerto de Render o el puerto por defecto
    uvicorn.run(app, host="0.0.0.0", port=port)
