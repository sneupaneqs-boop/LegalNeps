# Kanooni Sathi API. Build from the repo root:  docker compose up -d --build
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Build the search index and download the small search model into the image
# now, so the container answers in seconds after every restart.
RUN python scripts/prebuild_index.py

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
