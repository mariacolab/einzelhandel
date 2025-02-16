# Basis-Image auswählen
FROM python:3.10-slim AS base

# Arbeitsverzeichnis setzen
WORKDIR /app

# Allgemeine Abhängigkeiten installieren
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libmagic1 file
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
COPY . .
COPY . /app

RUN echo '#!/bin/sh' > /start.sh && \
    echo 'echo "Fixing /etc/davfs2/secrets permissions..."' >> /start.sh && \
    echo 'chmod 600 /etc/davfs2/secrets' >> /start.sh && \
    echo 'echo "Trying to mount WebDAV..."' >> /start.sh && \
    echo 'mount -t davfs http://host.docker.internal:8081 /mnt/gdrive || echo "Mount failed!"' >> /start.sh && \
    echo 'ls -lah /mnt/gdrive' >> /start.sh && \
    echo 'gunicorn --bind 0.0.0.0:5007 app:app &' >> /start.sh && \
    echo 'exec python3 subscriber.py' >> /start.sh && \
    chmod +x /start.sh

# Standardbefehl für Produktion
CMD ["/bin/sh", "/start.sh"]
# Standardbefehl für Produktion
#CMD ["gunicorn", "--bind", "0.0.0.0:5007", "app:app"]
