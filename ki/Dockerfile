# ---- Base Stage mit CUDA-Unterstützung ----
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04 AS base

# Verhindere interaktive Eingaben während der Installation
ENV DEBIAN_FRONTEND=noninteractive

# Aktualisieren und notwendige Pakete installieren, inklusive deadsnakes-PPA für Python 3.10
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
      python3.10 \
      python3.10-venv \
      python3.10-dev \
      python3-pip \
      gcc \
      libpq-dev \
      libmagic1 \
      file \
      libgl1 \
      libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Setze den Symlink, damit "python" auf Python 3.10 zeigt
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Arbeitsverzeichnis festlegen
WORKDIR /workspace

# Kopiere die requirements.txt und installiere die Python-Abhängigkeiten
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-pip && \
    python3 -m pip install --upgrade --force-reinstall pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# ---- Production Stage ----
FROM base AS production

# Kopiere den gesamten Applikationscode in das Image
COPY . /workspace

# Standardbefehl für die Produktion (hier: Gunicorn-Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5006", "app:app"]
