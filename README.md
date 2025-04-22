# 🧠 Metaflowia - Backend

Bienvenido al repositorio backend de **Metaflowia**, una API RESTful construida con **FastAPI** y conectada a **MongoDB Atlas**. Esta app gestiona usuarios, registros y operaciones de una plataforma que busca fusionar tecnología, comunidad y bienestar.

## 🚀 Tecnologías utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) – Framework moderno, rápido y minimalista para construir APIs.
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) – Base de datos NoSQL en la nube.
- [Motor](https://motor.readthedocs.io/en/stable/) – Driver async de MongoDB para Python.
- [Render](https://render.com) – Hosting para el despliegue del backend.

## 🔌 Endpoints principales

Visita la [documentación Swagger](https://metaflowia.onrender.com/docs) generada automáticamente por FastAPI.

Ejemplo de rutas disponibles:

- `GET /usuarios` - Lista todos los usuarios
- `POST /usuarios` - Crea un nuevo usuario
- `PUT /usuarios/{id}` - Actualiza un usuario
- `DELETE /usuarios/{id}` - Elimina un usuario

## ⚙️ Variables de entorno

Para correr el proyecto localmente, necesitás un archivo `.env` con lo siguiente:

```env
MONGO_URL=mongodb+srv://<usuario>:<password>@cluster.mongodb.net
DATABASE_NAME=metaflowia
