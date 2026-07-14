# Multi-stage build for smaller image size
FROM python:3.13-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.13-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app.py .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set Python to unbuffered mode for proper logging
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the application
CMD ["python", "app.py"]
