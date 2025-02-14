# NVIDIA CUDA 12.3.2 + CuDNN 9.3+ (Runtime-Image für YOLO)
FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 AS base

# Setze Umgebungsvariablen für NVIDIA (nur für YOLO relevant)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=""

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

# ---- Production Stage ----
FROM base AS production

# Kopiere den gesamten Applikationscode in das Image
COPY . /workspace

# Standardbefehl für die Produktion (hier: Gunicorn-Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]
