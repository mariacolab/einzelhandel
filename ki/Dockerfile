# NVIDIA CUDA 12.3.2 + CuDNN 9.3+ (Runtime-Image für YOLO)
FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 AS base

# Setze Umgebungsvariablen für NVIDIA (nur für YOLO relevant)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/workspace"

# Installiere Python 3.10 + Pip + Systempakete
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip \
    libgl1-mesa-glx libglib2.0-0 && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*


# Arbeitsverzeichnis setzen
WORKDIR /workspace

# Installiere Python-Abhängigkeiten (einschließlich aio-pika)
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Installiere TensorFlow **ohne GPU**
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install tensorflow-cpu==2.18.0

# Installiere PyTorch mit GPU-Unterstützung (nur für YOLO)
RUN python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Davfs2 und WebDAV-Setup direkt in den Container einbauen
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends davfs2 && \
    mkdir -p /mnt/gdrive && \
    touch /etc/davfs2/secrets && \
    echo "http://host.docker.internal:8081 webdav_user 1okivI54avrEC0DQv5trz42w9u5kgEZD7vPssLW" > /etc/davfs2/secrets && \
    chmod 600 /etc/davfs2/secrets && \
    chown root:root /etc/davfs2/secrets

# Installiere Supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Konfiguriere Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Starte Supervisor als Hauptprozess
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# ---- Production Stage ----
FROM base AS production

# Kopiere den gesamten Applikationscode in das Image
COPY . /workspace

#RUN echo '#!/bin/sh' > /start.sh && \
#    echo 'echo "Fixing /etc/davfs2/secrets permissions..."' >> /start.sh && \
#    echo 'chmod 600 /etc/davfs2/secrets' >> /start.sh && \
#    echo 'echo "Trying to mount WebDAV..."' >> /start.sh && \
#    echo 'mount -t davfs http://host.docker.internal:8081 /mnt/gdrive -o rw,allow-other,gid=1000,dir_mode=0777,file_mode=0777 || echo "Mount failed!"' >> /start.sh && \
#    echo 'ls -lah /mnt/gdrive' >> /start.sh && \
#    echo 'gunicorn --bind 0.0.0.0:5006 app:app &' >> /start.sh && \
#    echo 'exec python3 subscriber.py' >> /start.sh && \
#    chmod +x /start.sh

# Standardbefehl für Produktion
CMD ["/bin/sh", "/workspace/start.sh"]
# Standardbefehl für die Produktion (hier: Gunicorn-Server)
#CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]
