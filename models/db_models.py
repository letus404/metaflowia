from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.db_database import Base

class User(Base):
    __tablename__ = "users"  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(30), default="")
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String(255))
    role = Column(String(20), default="invitado")
