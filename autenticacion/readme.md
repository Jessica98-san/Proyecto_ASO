# Servicio 4 - Servicio de Autenticación

## Descripción
Este servicio proporciona autenticación y autorización para el sistema, implementando las tres opciones del requisito:

1. **Autenticación simple con usuarios simulados**
2. **Configuración mediante variables de entorno**
3. **Logging de peticiones**

## Tecnología
- **Lenguaje**: Python 3.11
- **Framework**: FastAPI
- **Autenticación**: JWT (JSON Web Tokens)
- **Puerto**: 8001

## Características

### Autenticación
- Sistema de login con usuarios simulados
- Generación de tokens JWT
- Validación de tokens
- Control de acceso basado en roles (RBAC)

### Usuarios Predefinidos

| Usuario   | Contraseña | Rol      | Descripción        |
|-----------|------------|----------|--------------------|
| admin     | admin123   | admin    | Administrador      |
| usuario1  | user123    | usuario  | Usuario estándar   |
| usuario2  | user456    | usuario  | Usuario estándar   |
| invitado  | guest      | invitado | Acceso limitado    |

### Variables de Entorno

| Variable            | Descripción                      | Valor por defecto                    |
|---------------------|----------------------------------|--------------------------------------|
| JWT_SECRET_KEY      | Clave secreta para firmar JWT    | clave_secreta_proyecto_aso_2024      |
| TOKEN_EXPIRE_MINUTES| Tiempo de expiración del token   | 30                                   |
| AUTH_SERVICE_PORT   | Puerto del servicio              | 8001                                 |
| ENVIRONMENT         | Entorno de ejecución             | development                          |

### Logging de Peticiones
El servicio registra automáticamente todas las peticiones:
- Timestamp
- Método HTTP
- Path
- IP del cliente
- User-Agent
- Código de respuesta
- Tiempo de procesamiento

## Endpoints

### Públicos

| Método | Endpoint   | Descripción                      |
|--------|------------|----------------------------------|
| GET    | /health    | Health check del servicio        |
| POST   | /login     | Iniciar sesión                   |
| POST   | /register  | Registrar nuevo usuario          |
| GET    | /config    | Ver configuración del servicio   |
| GET    | /stats     | Estadísticas del servicio        |

### Protegidos (requieren token)

| Método | Endpoint   | Descripción                      | Rol requerido |
|--------|------------|----------------------------------|---------------|
| GET    | /validate  | Validar token JWT                | Cualquiera    |
| POST   | /validate  | Validar token JWT                | Cualquiera    |
| GET    | /users     | Listar todos los usuarios        | admin         |
| GET    | /logs      | Ver logs de peticiones           | admin         |

## Uso

### Iniciar Sesión
```bash
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user_info": {
    "username": "admin",
    "nombre": "Administrador",
    "email": "admin@sistema.com",
    "rol": "admin"
  }
}
```

### Validar Token
```bash
curl -X GET http://localhost:8001/validate \
  -H "Authorization: Bearer <tu_token>"
```

### Registrar Usuario
```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "password": "mipassword",
    "nombre": "Nuevo Usuario",
    "email": "nuevo@email.com"
  }'
```

### Ver Estadísticas
```bash
curl http://localhost:8001/stats
```

### Ver Logs (solo admin)
```bash
curl http://localhost:8001/logs?limit=50 \
  -H "Authorization: Bearer <token_admin>"
```

## Ejecución Local

### Sin Docker
```bash
cd autenticacion
pip install -r requirements.txt
fastapi run auth_server.py --port 8001
```

### Con Docker
```bash
docker build -t auth-service .
docker run -p 8001:8001 auth-service
```

### Con Docker Compose (Proyecto completo)
```bash
# Desde la raíz del proyecto
docker compose up --build
```

## Estructura de Archivos

```
autenticacion/
├── Dockerfile          # Imagen Docker del servicio
├── requirements.txt    # Dependencias Python
├── auth_server.py      # Código principal del servicio
└── readme.md          # Esta documentación
```

## Integración con otros servicios

### Backend (Servicio 1)
El backend se conecta al servicio de autenticación para:
- Validar tokens en endpoints protegidos
- Identificar el usuario que realiza operaciones

### Frontend (Servicio 3)
El frontend utiliza el servicio para:
- Login/logout de usuarios
- Almacenamiento de tokens en localStorage
- Peticiones autenticadas al backend

## Documentación API
Accede a la documentación interactiva en:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Autor
**Servicio 4 - Autenticación/Configuración/Logs**  
Proyecto Grupal 2 - Despliegue de servicios usando Docker