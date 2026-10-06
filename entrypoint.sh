#!/bin/sh
# Start uvicorn with optional TLS — set SSL_CERTFILE + SSL_KEYFILE to enable HTTPS.
# Any arguments replace the uvicorn command (docker-compose.dev.yml uses this for --reload).
set -e

# The container starts as root only to hand /data to the runtime user, then drops
# to PUID:PGID for good. Left unset, they default to the owner of the media folder,
# which is the user that must be able to write there — so an install upgraded from
# `user: root` keeps working without editing its compose file. A media folder owned
# by root falls back to the image's own unprivileged appuser.
if [ "$(id -u)" = "0" ]; then
    MEDIA_DIR="${MEDIA_ROOT:-/media}"
    if [ -z "$PUID" ] && [ -d "$MEDIA_DIR" ] && [ "$(stat -c %u "$MEDIA_DIR")" != "0" ]; then
        PUID="$(stat -c %u "$MEDIA_DIR")"
        PGID="${PGID:-$(stat -c %g "$MEDIA_DIR")}"
    fi
    if [ -z "$PUID" ]; then
        echo "WARNING: PUID unset and $MEDIA_DIR is missing or owned by root, running as" \
            "appuser, which may not be able to write there. Set PUID/PGID to its owner."
    fi
    PUID="${PUID:-$(id -u appuser)}"
    PGID="${PGID:-$(id -g appuser)}"
    if [ "$PUID" = "0" ]; then
        echo "WARNING: PUID=0 — Hoard runs as root, with full rights on every mounted volume"
    else
        mkdir -p /data
        chown -R "$PUID:$PGID" /data
        # HOME stays /root otherwise, which the runtime user cannot write (yt-dlp cache).
        export HOME=/tmp
        exec setpriv --reuid="$PUID" --regid="$PGID" --clear-groups "$0" "$@"
    fi
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

ARGS="backend.main:app --host 0.0.0.0 --port 8000"

if [ -n "$SSL_CERTFILE" ] && [ -n "$SSL_KEYFILE" ]; then
    echo "HTTPS enabled: certfile=$SSL_CERTFILE keyfile=$SSL_KEYFILE"
    ARGS="$ARGS --ssl-certfile $SSL_CERTFILE --ssl-keyfile $SSL_KEYFILE"
else
    echo "HTTP mode (set SSL_CERTFILE + SSL_KEYFILE to enable HTTPS)"
fi

exec uvicorn $ARGS
