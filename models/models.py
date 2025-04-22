# Importa los paquetes necesarios
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import Optional
from bson import ObjectId

# Contexto de CryptContext para manejar la encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo de datos para el Usuario
class UserInDB(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = ""
    disabled: Optional[bool] = False
    hashed_password: str  # La contraseña será almacenada como un hash
    role: str = "invitado"

    class Config:
        # Permite manejar ObjectId como string
        json_encoders = {
            ObjectId: str
        }