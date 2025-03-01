# Verwende ein schlankes Python-Image
FROM python:3.9-slim

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Rest des Quellcodes kopieren
COPY . .

# Exponiere den benötigten Port (hier 5011 für die SocketIO-Anwendung)
EXPOSE 5015

# Starte die Anwendung
CMD ["python3", "watch_folder.py"]
