# Basisimage
FROM python:3.10-slim AS base

# Setze Umgebungsvariablen
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/workspace"

# Installation Systempakete
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /workspace

# Installation Python-Abhängigkeiten
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install watchdog

# Installiere TensorFlow **ohne GPU**
RUN python3 -m pip install tensorflow-cpu==2.18.0

# Installiere PyTorch mit GPU-Unterstützung (nur für YOLO)
RUN python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# ---- Production Stage ----
FROM base AS production

# Kopiert den Code der KI in das Image
COPY . /workspace

# Startbefehl
CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]

