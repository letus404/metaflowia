from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import pymysql

# Cargar las variables de entorno
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path)

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Esto le dice a SQLAlchemy que use pymysql como reemplazo de MySQLdb.
pymysql.install_as_MySQLdb()

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Crear la clase base para los modelos
Base = declarative_base()

# Crear la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)