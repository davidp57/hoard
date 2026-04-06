#!/bin/sh
# Start uvicorn with optional TLS — set SSL_CERTFILE + SSL_KEYFILE to enable HTTPS.
set -e

ARGS="backend.main:app --host 0.0.0.0 --port 8000"

if [ -n "$SSL_CERTFILE" ] && [ -n "$SSL_KEYFILE" ]; then
    echo "HTTPS enabled: certfile=$SSL_CERTFILE keyfile=$SSL_KEYFILE"
    ARGS="$ARGS --ssl-certfile $SSL_CERTFILE --ssl-keyfile $SSL_KEYFILE"
else
    echo "HTTP mode (set SSL_CERTFILE + SSL_KEYFILE to enable HTTPS)"
fi

exec uvicorn $ARGS
