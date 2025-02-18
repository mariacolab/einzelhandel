# NVIDIA CUDA 12.3.2 + CuDNN 9.3+ (Runtime-Image für YOLO)
FROM python:3.10-slim AS base

# Setze Umgebungsvariablen für NVIDIA (nur für YOLO relevant)
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/workspace"

# Installiere Python 3.10 + Pip + Systempakete
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /workspace

# Installiere Python-Abhängigkeiten (einschließlich aio-pika)
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install watchdog

# Installiere TensorFlow **ohne GPU**
RUN python3 -m pip install tensorflow-cpu==2.18.0

# Installiere PyTorch mit GPU-Unterstützung (nur für YOLO)
RUN python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Installiere Supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Konfiguriere Supervisor
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Starte Supervisor als Hauptprozess
#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# ---- Production Stage ----
FROM base AS production

# Kopiere den gesamten Applikationscode in das Image
COPY . /workspace

# Konfiguriere Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# Standardbefehl für die Produktion (hier: Gunicorn-Server)
#CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]
# Starte Supervisor als Hauptprozess
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
