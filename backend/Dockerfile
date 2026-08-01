# Backend Dockerfile for Google Cloud Run
# FastAPI application with uv package manager

FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS builder

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Install the project itself
RUN uv sync --frozen --no-dev

# =============================================================================
# Production Runtime
# =============================================================================
FROM python:3.14-slim AS production

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Cloud Run sets PORT environment variable (defaults to 8080)
# The application must listen on 0.0.0.0:$PORT
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run database migrations and start FastAPI
# Migrations run once at startup, then the server starts
CMD ["/bin/sh", "-c", "uv run alembic upgrade head && uv run fastapi run app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
