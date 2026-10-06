FROM python:3.12-slim

# Install ffmpeg and unrar
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg unrar-free && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY pyproject.toml ./pyproject.toml
COPY entrypoint.sh ./entrypoint.sh

# Ensure the data volume is writable by the app user
# Fix potential Windows CRLF line endings in entrypoint.sh
RUN sed -i 's/\r//' /app/entrypoint.sh && \
    mkdir -p /data && chown appuser:appuser /data && chmod +x /app/entrypoint.sh && \
    command -v setpriv

# No USER here: entrypoint.sh starts as root only to hand /data to PUID:PGID, then
# drops to that user for good with setpriv (checked above, so a base image that
# loses it fails the build instead of the container).

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "\
import urllib.request, os, ssl; \
s = os.environ.get('SSL_CERTFILE', ''); \
ctx = ssl._create_unverified_context() if s else None; \
urllib.request.urlopen(('https' if s else 'http') + '://localhost:8000/healthz', context=ctx)" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
