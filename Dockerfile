FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
# Provide your own config.yaml at runtime (mounted) or bake it in below.
COPY config.example.yaml ./config.example.yaml

# jobs.db lives here; mount a volume to persist dedupe state across restarts.
VOLUME ["/app/data"]
ENV JOBS_DB_PATH=/app/data/jobs.db

CMD ["python", "-m", "src.main"]
