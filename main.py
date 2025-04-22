from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from passlib.context import CryptContext
from METAFLOWIA.backend.routers.user_router import user_router
from METAFLOWIA.backend.db.database import users_collection
from METAFLOWIA.backend.routers.user_router import get_password_hash
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

app = FastAPI(
    title="User API",
    description="Gestión de usuarios (registro, login, invitado) con MongoDB",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_user():
    existing_user = await users_collection.find_one({"username": "admin"})
    if not existing_user:
        hashed_password = get_password_hash("admin")
        new_user = {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Administrador",
            "role": "admin",
            "disabled": False,
            "hashed_password": hashed_password
        }
        await users_collection.insert_one(new_user)

@app.on_event("startup")
async def on_startup():
    await create_default_user()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router, tags=["users"])
# Listo para ejecutarse con: uvicorn main:app --reload