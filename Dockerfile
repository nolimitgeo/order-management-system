# Lightweight image for the Order Tracker backend + frontend
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (Docker caches this layer when code changes)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ backend/
COPY frontend/ frontend/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "-m", "backend.app"]
