FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1+cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY backend .
COPY evaluation /evaluation

EXPOSE 8000

# Railway uses $PORT; default to 8000 for local Docker Compose
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
