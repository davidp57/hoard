FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY entrypoint.sh ./entrypoint.sh

# Ensure the data volume is writable by the app user
RUN mkdir -p /data && chown appuser:appuser /data && chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "\
import urllib.request, os, ssl; \
s = os.environ.get('SSL_CERTFILE', ''); \
ctx = ssl._create_unverified_context() if s else None; \
urllib.request.urlopen(('https' if s else 'http') + '://localhost:8000/api/files?path=', context=ctx)" || exit 1

CMD ["/app/entrypoint.sh"]
