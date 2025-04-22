from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from bson import ObjectId
import os
from motor.motor_asyncio import AsyncIOMotorClient
from METAFLOWIA.backend.models.models import UserInDB 
from METAFLOWIA.backend.schemas.schemas import UserCreate, UserResponse
from METAFLOWIA.backend.db.database import db, MONGO_DB, users_collection
from dotenv import load_dotenv
from pathlib import Path
from typing import List

# Cargamos las variables de entorno
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path)

# Variables de entorno
SECRET_KEY = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if MONGO_DB is None:
    raise ValueError("DATABASE_NAME no está definida en el archivo .env")


# Para obtener la contraseña encriptada
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para los endpoints
user_router = APIRouter()

# OAuth2PasswordBearer es el esquema para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelos para los datos
class User(BaseModel):
    username: str
    email: str
    full_name: str = ""
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Función para encriptar contraseñas
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Función para crear un nuevo usuario
async def create_user(user: UserInDB):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_dict = user.dict()
    
    await db.users.insert_one(user_dict)

# Función para obtener un usuario
async def get_user(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return UserInDB(**user)
    return None

# Verificar si el token es válido
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_username_or_email(identifier: str):
    # Usamos $or para buscar por username o email
    user = await users_collection.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    if user:
        return UserInDB(**user)  # Regresamos un modelo UserInDB
    return None

@user_router.get("/")
async def root():
    return {"message": "BACKEND CORRIENDO, BIENVENID@ A METAFLOWIA ✨"}

# Ruta para el login
@user_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"🛂 Intentando login con username: {form_data.username}")

    # Buscar al usuario por username o email
    user = await get_user_by_username_or_email(form_data.username)
    if user is None:
        print("❌ Usuario no encontrado")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Verificación de la contraseña
    if not pwd_context.verify(form_data.password, user.hashed_password):
        print("❌ Contraseña incorrecta")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Creación del token de acceso
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    print(f"✅ Login exitoso para: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

# Ruta para crear un nuevo usuario
@user_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Revisa si el usuario ya existe
    if await db.users.find_one({"username": user.username}):
        print("Usuario ya registrado:", user.username)  # Agregamos un mensaje en consola
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Llama a la función que registra al usuario
    user_in_db = UserInDB(**user.dict(), hashed_password=get_password_hash(user.password))
    
    try:
        await create_user(user_in_db)  # Intenta crear el usuario
        print(f"Usuario agregado exitosamente: {user.username}")  # Mensaje en consola
    except Exception as e:
        print(f"Error al agregar usuario: {str(e)}")  # Si hay algún error al agregar el usuario
        raise HTTPException(status_code=500, detail="Error al agregar el usuario")
    
    return user

# Ruta para ingreso como invitado
@user_router.post("/guest", response_model=Token)
async def login_as_guest():
    username = "guest"
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Obtener todos los usuarios
@user_router.get("/get_users", response_model=List[UserInDB])
async def get_users():
    users = await users_collection.find().to_list(20)  # Esto obtiene los primeros 20 usuarios
    return users

# Asumiendo que tienes un modelo de Usuario en db.models como UserInDB
__all__ = ["user_router"]