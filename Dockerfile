# Multi-stage Dockerfile for production deployment
# Builds both backend (FastAPI/uv) and frontend (Next.js/Bun)
# Optimized for AWS Cloud Run and Google Cloud Run deployments

# =============================================================================
# Stage 1: Backend - Build Python dependencies
# =============================================================================
FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS backend-builder

WORKDIR /app/backend

# Copy dependency files first for better caching
COPY backend/pyproject.toml backend/uv.lock ./

# Install production dependencies only
RUN uv sync --frozen --no-dev --no-install-project

# Copy backend source code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

# Install the project itself
RUN uv sync --frozen --no-dev

# =============================================================================
# Stage 2: Frontend - Build Next.js application
# =============================================================================
FROM oven/bun:1 AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package.json frontend/bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/next.config.ts ./
COPY frontend/tsconfig.json ./
COPY frontend/tailwind.config.ts ./
COPY frontend/postcss.config.mjs ./
COPY frontend/components.json ./

# Build the Next.js application (creates standalone output)
RUN bun run build

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM python:3.14-slim AS production

# Install Node.js runtime for Next.js standalone server
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy backend from builder
COPY --from=backend-builder --chown=appuser:appuser /app/backend /app/backend

# Copy frontend from builder
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/.next/standalone /app/frontend
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/.next/static /app/frontend/.next/static
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/public /app/frontend/public

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_ENV=production \
    PORT=8000 \
    HOSTNAME=0.0.0.0

# Expose ports
# For Cloud Run: Only one port can be used, so we use PORT env var
# Default is 8000 for backend, frontend proxies API requests internally
EXPOSE ${PORT}

# Switch to non-root user
USER appuser

# Health check for Cloud Run and load balancers
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Start script that runs both services
COPY <<'STARTSCRIPT' /app/start.sh
#!/bin/bash
set -e

# Run database migrations (skip if DATABASE_URL not set or migration fails gracefully)
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    cd /app/backend
    uv run alembic upgrade head || echo "Warning: Migration failed, continuing anyway..."
else
    echo "DATABASE_URL not set, skipping migrations..."
fi

# Start both services
echo "Starting services on port $PORT..."

# Start backend in background
cd /app/backend
uv run fastapi run app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
BACKEND_PID=$!

# Start frontend - it will proxy /api/* to backend via rewrites
cd /app/frontend
bun server.js --port ${FRONTEND_PORT:-3000} --hostname 0.0.0.0 &
FRONTEND_PID=$!

# Wait for any process to exit
wait -n $BACKEND_PID $FRONTEND_PID

# Exit with status of process that exited first
exit $?
STARTSCRIPT

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
