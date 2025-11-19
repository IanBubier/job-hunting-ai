# Dockerfile for Job Hunting AI Web Tool
FROM python:3.12-slim

# Install minimal system deps required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip
RUN pip install -U -r backend/requirements.txt

# Pre-download ML model into image layer (don't fail build on network issues)
RUN python backend/download_model.py || true

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

# Use Gunicorn with the wsgi entrypoint. Cloud providers set PORT at runtime.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app", "--workers", "2", "--timeout", "120"]
