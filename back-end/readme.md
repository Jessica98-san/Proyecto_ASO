# ⚙️ Servicio 1: API Backend (FastAPI)

Este módulo contiene la lógica principal del sistema, encargado de la gestión de peticiones y la validación de datos.

## 🚀 Responsabilidades del Servicio
* **Recepción de Datos:** Gestión de mensajes a través de endpoints REST.
* **Validación:** Uso de modelos Pydantic para asegurar la integridad de la información.
* **Orquestación:** Configuración de contenedor independiente mediante Docker.

## 🛠️ Tecnologías
* **Framework:** FastAPI
* **Lenguaje:** Python 3.11
* **Contenedor:** Docker (Image: python:3.11-slim)

## 📁 Archivos Clave
* `server.py`: Lógica de los endpoints (`/health`, `/save`, `/data`).
* `Dockerfile`: Configuración del entorno de ejecución del backend.
* `requirements.txt`: Dependencias necesarias (FastAPI, Psycopg, Uvicorn).

---
**Desarrollado por:** Isaac Morales
