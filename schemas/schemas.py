from pydantic import BaseModel
from typing import Optional

# Modelo para crear un nuevo usuario (entrada)
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    password: str  # El password será enviado en texto plano y luego será encriptado
    role: str | None = "invitado"

# Modelo para respuesta de usuario (salida)
class UserResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False  # Si el usuario está deshabilitado o no
    role: Optional[str] = "invitado"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
