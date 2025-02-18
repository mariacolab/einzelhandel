# Use Node.js as the base image
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Kopiere package.json und package-lock.json aus `frontend_einzelhandel`
COPY frontend_einzelhandel/package.json frontend_einzelhandel/package-lock.json ./

# Install Angular CLI und die notwendigen Pakete
RUN npm install -g @angular/cli

# Install dependencies
RUN npm install
RUN npm install --legacy-peer-deps \
    @angular/material @angular/cdk @angular/animations \
    ngx-webcam @zxing/ngx-scanner @zxing/browser @zxing/library


# Kopiere den gesamten Code ins Arbeitsverzeichnis
COPY frontend_einzelhandel/. .

# Build the Angular application
RUN npm run build

# Install and use http-server to serve the built Angular app
RUN npm install -g http-server

# Serve the Angular app
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200"]