# Multi-stage Dockerfile for FastAPI Backend
# Supports: development, staging, production

# Base stage - common dependencies
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Development stage
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    watchfiles \
    pytest \
    pytest-asyncio \
    httpx

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with auto-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Staging stage
FROM base AS staging

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with limited workers for memory efficiency
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]


# Production stage
FROM base AS production

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run with production settings (limited workers for older PC)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "warning"]
