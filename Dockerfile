FROM python:3.12-slim

WORKDIR /app

# Install system deps if needed (safe to keep minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Fly.io expects the app to listen on 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

