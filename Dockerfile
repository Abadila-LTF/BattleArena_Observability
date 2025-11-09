# Multi-stage build for smaller final image

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder to a location accessible by battlearena user
COPY --from=builder /root/.local /home/battlearena/.local

# Make sure scripts in .local are usable
ENV PATH=/home/battlearena/.local/bin:$PATH

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd -m -u 1000 battlearena && \
    chown -R battlearena:battlearena /app && \
    chown -R battlearena:battlearena /home/battlearena/.local

USER battlearena

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
