FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    cmake \
    build-essential \
    gfortran \
    git \
    wget \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libx11-dev \
    libgtk-3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and set permissions for directories
RUN mkdir -p /app/face_embeddings && \
    mkdir -p /app/staticfiles && \
    mkdir -p /app/data/db && \
    mkdir -p /app/data/media && \
    chmod -R 777 /app

# Install dependencies in specific order
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone and install face_recognition_models
RUN git clone https://github.com/ageitgey/face_recognition_models.git && \
    cd face_recognition_models && \
    pip install . && \
    cd .. && \
    rm -rf face_recognition_models

# Install face_recognition
RUN pip install --no-cache-dir face_recognition

# Copy project files
COPY ./attendance /app

# Explicitly set permissions after copying
RUN chmod -R 777 /app

EXPOSE 8000

# Use Gunicorn to run the application
CMD ["gunicorn", "attendance.wsgi:application", "--bind", "0.0.0.0:8000"]
