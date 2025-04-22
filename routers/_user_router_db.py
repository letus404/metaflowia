from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional, List

from models.db_models import User as DBUser
from schemas.schemas import UserCreate, UserResponse, Token, TokenData
from db.db_database import SessionLocal

import os
from dotenv import load_dotenv
from pathlib import Path


# Cargar .env
dotenv_path = os.path.join(Path(__file__).resolve().parent.parent, ".env")
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

user_router = APIRouter()


# ---------- UTILS ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username_or_email(db: Session, identifier: str):
    return db.query(DBUser).filter(
        (DBUser.username == identifier) | (DBUser.email == identifier)
    ).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username_or_email(db, username)
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(current_user: DBUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tenés permisos de administrador")
    return current_user

# ---------- ENDPOINTS ----------

@user_router.get("/")
def root():
    return {"message": "API funcionando con MySQL"}

@user_router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = get_user_by_username_or_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username_or_email(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    new_user = DBUser(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@user_router.post("/register_guest", response_model=UserResponse)
def register_guest(db: Session = Depends(get_db)):
    # Generar un nombre de usuario invitado único
    count = db.query(DBUser).count()
    guest_username = f"guest{count + 1}"
    guest_email = f"{guest_username}@guest.local"
    password = "invitado"  # Contraseña por defecto (puede ser aleatoria)

    hashed_password = get_password_hash(password)

    new_user = DBUser(
        username=guest_username,
        email=guest_email,
        full_name="guest",
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@user_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: DBUser = Depends(get_current_user)):
    return current_user

@user_router.get("/users", response_model=List[UserResponse])
def get_all_users(skip: int = 0, limit: int = 10, 
                  db: Session = Depends(get_db), 
                  current_user: DBUser = Depends(get_admin_user)):
    return db.query(DBUser).offset(skip).limit(limit).all()