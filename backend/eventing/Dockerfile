# Basis-Image auswählen
FROM python:3.10-slim AS base

# Arbeitsverzeichnis setzen
WORKDIR /app

# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Davfs2 und WebDAV-Setup direkt in den Container einbauen
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends davfs2 && \
    mkdir -p /mnt/gdrive && \
    touch /etc/davfs2/secrets && \
    echo "http://host.docker.internal:8081 webdav_user 1okivI54avrEC0DQv5trz42w9u5kgEZD7vPssLW" > /etc/davfs2/secrets && \
    chmod 600 /etc/davfs2/secrets && \
    chown root:root /etc/davfs2/secrets

# ---- Build für Tests ----
FROM base AS test

# Zusätzliche Abhängigkeiten für Tests installieren
RUN pip install pytest pytest-flask

# Anwendung und Testdateien kopieren
COPY . .

COPY tests /app/tests

# Standardbefehl für Tests
CMD ["pytest", "tests/"]

# ---- Build für normale Ausführung ----
FROM base AS production

# Anwendung kopieren
COPY . /app

# Startscript erstellen, um WebDAV zu mounten und die App zu starten
#RUN echo '#!/bin/sh' > /start.sh && \
#    echo 'echo "Fixing /etc/davfs2/secrets permissions..."' >> /start.sh && \
#    echo 'chmod 600 /etc/davfs2/secrets' >> /start.sh && \
#    echo 'echo "Trying to mount WebDAV..."' >> /start.sh && \
#    echo 'mount -t davfs http://host.docker.internal:8081 /mnt/gdrive -o rw,allow-other,gid=1000,dir_mode=0777,file_mode=0777 || echo "Mount failed!"' >> /start.sh && \
#    echo 'ls -lah /mnt/gdrive' >> /start.sh && \
#    echo 'exec gunicorn --bind 0.0.0.0:5005 app:app' >> /start.sh && \
#    chmod +x /start.sh

# Standardbefehl für Produktion
CMD ["/bin/sh", "/app/start.sh"]
