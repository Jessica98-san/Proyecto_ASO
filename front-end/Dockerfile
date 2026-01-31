# Contruccion del frontend web
FROM node:22-alpine

# Crear directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json .

# Instalar dependencias
RUN npm install

# Copiar el resto de la aplicacion
COPY . .

EXPOSE 5173

CMD ["npm", "run", "prod"]