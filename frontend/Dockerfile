# Frontend Dockerfile for Google Cloud Run
# Next.js application with Bun runtime

FROM oven/bun:1 AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code and config
COPY src ./src
COPY public ./public
COPY next.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.ts ./
COPY postcss.config.mjs ./
COPY components.json ./

# Build the Next.js application (creates standalone output)
RUN bun run build

# =============================================================================
# Production Runtime
# =============================================================================
FROM node:20-slim AS production

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy standalone output from builder
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static
COPY --from=builder --chown=appuser:appuser /app/public ./public

# Set environment variables
ENV NODE_ENV=production

# Cloud Run sets PORT environment variable (defaults to 8080)
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/ || exit 1

# Start Next.js standalone server
CMD ["node", "server.js"]
