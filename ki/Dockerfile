# Basis-Image auswählen
FROM python:3.10-slim AS base

# Arbeitsverzeichnis setzen
WORKDIR /workspace

# Allgemeine Abhängigkeiten installieren
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libmagic1 file
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Build für Tests ----
FROM base AS test

# Zusätzliche Abhängigkeiten für Tests installieren
RUN pip install pytest pytest-flask

# Anwendung und Testdateien kopieren
COPY . .

COPY tests /workspace/tests

# Standardbefehl für Tests
CMD ["pytest", "tests/"]

# ---- Build für normale Ausführung ----
FROM base AS production

# Anwendung kopieren
COPY . .

# Standardbefehl für Produktion
CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]
