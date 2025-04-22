from sqlalchemy.orm import Session
from .db_database import SessionLocal

# Función que proporciona una nueva sesión de base de datos
def get_db():
    db = SessionLocal()  # Se crea la sesión
    try:
        yield db  # Devolvemos la sesión
    finally:
        db.close()  # Cerramos la sesión cuando se termine su uso