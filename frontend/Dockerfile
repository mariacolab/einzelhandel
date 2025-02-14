# Use Node.js as the base image
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Kopiere package.json und package-lock.json aus `frontend_einzelhandel`
COPY frontend_einzelhandel/package.json frontend_einzelhandel/package-lock.json ./

# Install dependencies
RUN npm install

# Kopiere den gesamten Code ins Arbeitsverzeichnis
COPY frontend_einzelhandel/. .

# Build the Angular application
RUN npm run build

# Install and use http-server to serve the built Angular app
RUN npm install -g http-server

# Serve the Angular app
CMD ["npx", "http-server", "dist/frontend", "-p", "4200"]
