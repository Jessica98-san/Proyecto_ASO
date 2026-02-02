# Servicio 2 – Base de Datos (PostgreSQL)

Este servicio corresponde a la base de datos del sistema, implementada con **PostgreSQL** y gestionada mediante **Docker Compose**.  
Su objetivo es almacenar de forma persistente la información utilizada por el API REST del proyecto.

## Tecnologías utilizadas
- PostgreSQL 15
- Docker
- Docker Compose

## Configuración del servicio

El servicio de base de datos se define en el archivo `docker-compose.yml` de la siguiente manera:

```yaml
services:
  db_postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=admin
      - POSTGRES_DB=mensajeria
    volumes:
      - volumen_postgres:/var/lib/postgresql/data