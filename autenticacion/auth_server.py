"""
Servicio 4 - Servicio de Autenticación Simple
Este servicio proporciona autenticación básica con usuarios simulados,
generación de tokens JWT y registro de logs de peticiones.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import hashlib
import json

# Configuración de logging para registrar peticiones
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/auth.log') if os.path.exists('/app/logs') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Servicio de Autenticación",
    description="API de autenticación simple con usuarios simulados y logging de peticiones",
    version="1.0.0"
)

# Configuración mediante variables de entorno
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clave_secreta_proyecto_aso_2024")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "30"))
AUTH_SERVICE_PORT = int(os.getenv("AUTH_SERVICE_PORT", "8001"))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de datos simulada de usuarios
USUARIOS_SIMULADOS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "nombre": "Administrador",
        "email": "admin@sistema.com",
        "rol": "admin"
    },
    "usuario1": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "nombre": "Usuario Uno",
        "email": "usuario1@sistema.com",
        "rol": "usuario"
    },
    "usuario2": {
        "password_hash": hashlib.sha256("user456".encode()).hexdigest(),
        "nombre": "Usuario Dos",
        "email": "usuario2@sistema.com",
        "rol": "usuario"
    },
    "invitado": {
        "password_hash": hashlib.sha256("guest".encode()).hexdigest(),
        "nombre": "Invitado",
        "email": "invitado@sistema.com",
        "rol": "invitado"
    }
}

# Almacén de logs en memoria
LOGS_PETICIONES = []

# Modelos Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

class TokenValidationResponse(BaseModel):
    valid: bool
    username: Optional[str] = None
    rol: Optional[str] = None
    message: str

class LogEntry(BaseModel):
    timestamp: str
    method: str
    path: str
    client_ip: str
    user_agent: str
    status_code: int

class RegisterRequest(BaseModel):
    username: str
    password: str
    nombre: str
    email: str

# Security
security = HTTPBearer(auto_error=False)

# Middleware para logging de peticiones
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Procesar la petición
    response = await call_next(request)
    
    # Registrar la petición
    log_entry = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "path": str(request.url.path),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "status_code": response.status_code,
        "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
    }
    
    LOGS_PETICIONES.append(log_entry)
    
    # Mantener solo los últimos 1000 logs
    if len(LOGS_PETICIONES) > 1000:
        LOGS_PETICIONES.pop(0)
    
    logger.info(f"{log_entry['method']} {log_entry['path']} - {log_entry['status_code']} - {log_entry['processing_time_ms']:.2f}ms")
    
    return response

# Funciones auxiliares
def hash_password(password: str) -> str:
    """Genera hash SHA256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(username: str, rol: str) -> str:
    """Crea un token JWT con información del usuario"""
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "rol": rol,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expirado"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token inválido"}

# Endpoints

@app.get("/health")
def health_check():
    """Endpoint de health check del servicio de autenticación"""
    return {
        "status": "ok",
        "service": "autenticacion",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "token_expire_minutes": TOKEN_EXPIRE_MINUTES,
            "total_users": len(USUARIOS_SIMULADOS)
        }
    }

@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """
    Endpoint de inicio de sesión.
    Usuarios disponibles:
    - admin / admin123 (rol: admin)
    - usuario1 / user123 (rol: usuario)
    - usuario2 / user456 (rol: usuario)
    - invitado / guest (rol: invitado)
    """
    username = credentials.username.lower()
    
    if username not in USUARIOS_SIMULADOS:
        logger.warning(f"Intento de login fallido - usuario no existe: {username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    user = USUARIOS_SIMULADOS[username]
    password_hash = hash_password(credentials.password)
    
    if password_hash != user["password_hash"]:
        logger.warning(f"Intento de login fallido - contraseña incorrecta: {username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Generar token JWT
    token = create_jwt_token(username, user["rol"])
    
    logger.info(f"Login exitoso: {username} (rol: {user['rol']})")
    
    return LoginResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=TOKEN_EXPIRE_MINUTES * 60,
        user_info={
            "username": username,
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"]
        }
    )

@app.post("/validate", response_model=TokenValidationResponse)
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida un token JWT y retorna información del usuario"""
    if not credentials:
        return TokenValidationResponse(
            valid=False,
            message="No se proporcionó token"
        )
    
    result = verify_jwt_token(credentials.credentials)
    
    if result["valid"]:
        payload = result["payload"]
        return TokenValidationResponse(
            valid=True,
            username=payload["sub"],
            rol=payload["rol"],
            message="Token válido"
        )
    else:
        return TokenValidationResponse(
            valid=False,
            message=result["error"]
        )

@app.get("/validate")
def validate_token_get(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida un token JWT (método GET para facilitar pruebas)"""
    return validate_token(credentials)

@app.post("/register")
def register_user(user_data: RegisterRequest):
    """
    Endpoint para registrar nuevos usuarios (simulado).
    Los usuarios se guardan en memoria y se pierden al reiniciar el servicio.
    """
    username = user_data.username.lower()
    
    if username in USUARIOS_SIMULADOS:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    if len(user_data.password) < 4:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 4 caracteres")
    
    # Crear nuevo usuario
    USUARIOS_SIMULADOS[username] = {
        "password_hash": hash_password(user_data.password),
        "nombre": user_data.nombre,
        "email": user_data.email,
        "rol": "usuario"
    }
    
    logger.info(f"Nuevo usuario registrado: {username}")
    
    return {
        "message": "Usuario registrado exitosamente",
        "username": username,
        "rol": "usuario"
    }

@app.get("/users")
def list_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Lista todos los usuarios (solo para administradores)"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Se requiere autenticación")
    
    result = verify_jwt_token(credentials.credentials)
    
    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    if result["payload"]["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver la lista de usuarios")
    
    # Retornar usuarios sin las contraseñas
    users_list = [
        {
            "username": username,
            "nombre": data["nombre"],
            "email": data["email"],
            "rol": data["rol"]
        }
        for username, data in USUARIOS_SIMULADOS.items()
    ]
    
    return {"users": users_list, "total": len(users_list)}

@app.get("/logs")
def get_logs(limit: int = 100, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtiene los logs de peticiones recientes.
    Requiere autenticación con rol de administrador.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Se requiere autenticación")
    
    result = verify_jwt_token(credentials.credentials)
    
    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    if result["payload"]["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver los logs")
    
    # Retornar los últimos 'limit' logs
    recent_logs = LOGS_PETICIONES[-limit:] if limit < len(LOGS_PETICIONES) else LOGS_PETICIONES
    
    return {
        "logs": recent_logs,
        "total_logs": len(LOGS_PETICIONES),
        "returned": len(recent_logs)
    }

@app.get("/config")
def get_config():
    """
    Retorna la configuración actual del servicio mediante variables de entorno.
    Este endpoint demuestra el uso de configuración por variables de entorno.
    """
    return {
        "service_name": "Servicio de Autenticación",
        "version": "1.0.0",
        "configuration": {
            "JWT_SECRET_KEY": "***OCULTO***",
            "TOKEN_EXPIRE_MINUTES": TOKEN_EXPIRE_MINUTES,
            "AUTH_SERVICE_PORT": AUTH_SERVICE_PORT,
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
        },
        "features": {
            "jwt_authentication": True,
            "user_registration": True,
            "request_logging": True,
            "role_based_access": True
        }
    }

@app.get("/stats")
def get_stats():
    """Retorna estadísticas del servicio"""
    # Calcular estadísticas de los logs
    total_requests = len(LOGS_PETICIONES)
    
    if total_requests > 0:
        methods_count = {}
        status_codes = {}
        avg_time = 0
        
        for log in LOGS_PETICIONES:
            method = log["method"]
            status = log["status_code"]
            
            methods_count[method] = methods_count.get(method, 0) + 1
            status_codes[status] = status_codes.get(status, 0) + 1
            avg_time += log.get("processing_time_ms", 0)
        
        avg_time = avg_time / total_requests
    else:
        methods_count = {}
        status_codes = {}
        avg_time = 0
    
    return {
        "total_requests": total_requests,
        "total_users": len(USUARIOS_SIMULADOS),
        "requests_by_method": methods_count,
        "requests_by_status": status_codes,
        "average_response_time_ms": round(avg_time, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AUTH_SERVICE_PORT)
