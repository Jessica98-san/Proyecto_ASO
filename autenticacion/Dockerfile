# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Crear directorio para logs
RUN mkdir -p /app/logs

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY auth_server.py .

# Variables de entorno por defecto
ENV JWT_SECRET_KEY="clave_secreta_proyecto_aso_2024"
ENV TOKEN_EXPIRE_MINUTES=30
ENV AUTH_SERVICE_PORT=8001
ENV ENVIRONMENT=production

# Exponer puerto
EXPOSE 8001

# Comando de inicio
CMD ["fastapi", "run", "auth_server.py", "--host", "0.0.0.0", "--port", "8001"]
