import os
import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Cargar variables del archivo .env
load_dotenv()

app = FastAPI()

# 2. Configuración de la base de datos
# 2. Configuración de la base de datos (FORZADA AL PUERTO 5433)
DB_CONFIG = {
    "host": "host.docker.internal",
    "user": "postgres",
    "password": "admin",
    "dbname": "mensajeria",
    "port": "5433" 
}
# 3. Función para inicializar la conexión y crear la tabla
def init_db():
    try:
        # Conectamos usando los parámetros del .env
        connection = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY, 
                    mensaje TEXT, 
                    autor TEXT
                )
            """)
            connection.commit()
        print("✅ Conexión exitosa y tabla 'mensajes' lista.")
        return connection
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None

# 4. Intentar la conexión inicial
conn = init_db()

# 5. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Modelo de datos
class Mensaje(BaseModel):
    mensaje: str
    autor: str

# 7. Endpoints
@app.get("/health")
def health():
    global conn  # Corregido: primero declaramos global
    is_alive = False
    try:
        if conn and not conn.closed:
            # Hacemos una consulta rápida para ver si la base responde
            conn.execute("SELECT 1")
            is_alive = True
        else:
            # Si estaba cerrada, intentamos reconectar
            conn = init_db()
            is_alive = conn is not None
    except:
        is_alive = False
    
    return {
        "status": "ok", 
        "db_connected": is_alive,
        "database": DB_CONFIG["dbname"]
    }

@app.get("/data")
def data():
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensajes")
            return cursor.fetchall()
    except Exception as e:
        return {"error": str(e)}

@app.post("/save")
def save(mensaje: Mensaje):
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mensajes (mensaje, autor) VALUES (%s, %s)", 
                (mensaje.mensaje, mensaje.autor)
            )
            conn.commit()
            return {"status": "saved", "data": mensaje}
    except Exception as e:
        return {"error": str(e)}
