import os
import httpx
import psycopg
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

# 1. Cargar variables del archivo .env
load_dotenv()

app = FastAPI(
    title="API REST - Mensajería",
    description="Servicio 1 - API REST con integración de autenticación",
    version="1.0.0"
)

# 2. Configuración de la base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "host.docker.internal"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "dbname": os.getenv("DB_NAME", "mensajeria"),
    "port": os.getenv("DB_PORT", "5433")
}

# 3. URL del servicio de autenticación
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

# 4. Función para inicializar la conexión y crear la tabla
def init_db():
    try:
        connection = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY, 
                    mensaje TEXT, 
                    autor TEXT,
                    usuario TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
        print("✅ Conexión exitosa y tabla 'mensajes' lista.")
        return connection
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None

# 5. Intentar la conexión inicial
conn = init_db()

# 6. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 7. Modelo de datos
class Mensaje(BaseModel):
    mensaje: str
    autor: str

# 8. Función para validar token con el servicio de autenticación
async def verify_token(authorization: Optional[str] = None):
    """Verifica el token JWT con el servicio de autenticación"""
    if not authorization:
        return None
    
    try:
        # Extraer el token del header
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
        
        # Validar con el servicio de autenticación
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    return {
                        "username": data.get("username"),
                        "rol": data.get("rol")
                    }
        return None
    except Exception as e:
        print(f"Error validando token: {e}")
        return None

# 9. Endpoints

@app.get("/health")
def health():
    global conn
    is_alive = False
    auth_status = "desconocido"
    
    try:
        if conn and not conn.closed:
            conn.execute("SELECT 1")
            is_alive = True
        else:
            conn = init_db()
            is_alive = conn is not None
    except:
        is_alive = False
    
    # Verificar conexión con el servicio de autenticación
    try:
        with httpx.Client() as client:
            response = client.get(f"{AUTH_SERVICE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                auth_status = "conectado"
            else:
                auth_status = "error"
    except:
        auth_status = "no disponible"
    
    return {
        "status": "ok", 
        "db_connected": is_alive,
        "database": DB_CONFIG["dbname"],
        "auth_service": auth_status,
        "auth_url": AUTH_SERVICE_URL
    }

@app.get("/data")
def data():
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensajes ORDER BY id DESC")
            return cursor.fetchall()
    except Exception as e:
        return {"error": str(e)}

@app.post("/save")
async def save(mensaje: Mensaje, authorization: Optional[str] = Header(None)):
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    
    # Intentar obtener información del usuario autenticado
    user_info = await verify_token(authorization)
    usuario = user_info["username"] if user_info else "anónimo"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mensajes (mensaje, autor, usuario) VALUES (%s, %s, %s)", 
                (mensaje.mensaje, mensaje.autor, usuario)
            )
            conn.commit()
            return {
                "status": "saved", 
                "data": mensaje,
                "saved_by": usuario,
                "authenticated": user_info is not None
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/data/protected")
async def data_protected(authorization: str = Header(...)):
    """
    Endpoint protegido que requiere autenticación.
    Solo usuarios autenticados pueden acceder.
    """
    user_info = await verify_token(authorization)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensajes ORDER BY id DESC")
            mensajes = cursor.fetchall()
            return {
                "user": user_info,
                "data": mensajes,
                "total": len(mensajes)
            }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/data/{mensaje_id}")
async def delete_mensaje(mensaje_id: int, authorization: str = Header(...)):
    """
    Eliminar un mensaje. Requiere autenticación con rol de admin.
    """
    user_info = await verify_token(authorization)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    if user_info.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar mensajes")
    
    if not conn or conn.closed:
        return {"error": "Base de datos no conectada"}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM mensajes WHERE id = %s", (mensaje_id,))
            conn.commit()
            return {"status": "deleted", "id": mensaje_id, "deleted_by": user_info["username"]}
    except Exception as e:
        return {"error": str(e)}
