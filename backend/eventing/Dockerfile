# Basis-Image auswählen
FROM python:3.10-slim AS base

# Arbeitsverzeichnis setzen
WORKDIR /app

#COPY ../common /app/common
#COPY ../secrets /app/common/secrets
#RUN pip install ./common

# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
# Standardbefehl für Produktion
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "app:app"]