# von Maria  Schuster
# Basisimage
FROM python:3.10-slim AS base

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libmagic1 file

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---- Build für Tests ----
FROM base AS test

# zusätzliche Abhängigkeiten für Tests installieren
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

# Standardbefehl für Produktion
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]

