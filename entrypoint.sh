#!/bin/sh
# Start uvicorn with optional TLS — set SSL_CERTFILE + SSL_KEYFILE to enable HTTPS.
# Any arguments replace the uvicorn command (docker-compose.dev.yml uses this for --reload).
set -e

# The container starts as root only to hand /data to the runtime user, then drops
# to PUID:PGID for good. Left unset, PUID defaults to the owner of the media folder,
# the user that must be able to write there, so an install upgraded from
# `user: root` keeps working without editing its compose file. A media folder owned
# by root (a Synology shared folder often is, access going through ACLs) falls back
# to the image's own appuser — and, if appuser cannot write there either, to root
# with a warning rather than to an install that silently stops writing.
as_runtime_user() { setpriv --reuid="$PUID" --regid="$PGID" --clear-groups "$@"; }

if [ "$(id -u)" = "0" ]; then
    MEDIA_DIR="${MEDIA_ROOT:-/media}"
    if [ -z "$PGID" ] && [ -d "$MEDIA_DIR" ] && [ "$(stat -c %g "$MEDIA_DIR")" != "0" ]; then
        PGID="$(stat -c %g "$MEDIA_DIR")"
    fi
    PGID="${PGID:-$(id -g appuser)}"
    if [ -z "$PUID" ]; then
        if [ -d "$MEDIA_DIR" ] && [ "$(stat -c %u "$MEDIA_DIR")" != "0" ]; then
            PUID="$(stat -c %u "$MEDIA_DIR")"
        else
            PUID="$(id -u appuser)"
            if [ -d "$MEDIA_DIR" ] && ! as_runtime_user test -w "$MEDIA_DIR"; then
                echo "WARNING: $MEDIA_DIR is owned by root and appuser cannot write there:" \
                    "staying root. Set PUID/PGID to a user that can (on Synology, your DSM user)."
                PUID=0
            fi
        fi
    fi
    if [ "$PUID" = "0" ]; then
        echo "WARNING: running as root, with full rights on every mounted volume"
    else
        mkdir -p /data
        chown -R "$PUID:$PGID" /data
        # A key generated on the host is often readable by its creator only. Root can
        # still read it: hand the runtime user a private copy rather than crash-loop.
        if [ -n "$SSL_CERTFILE" ] && [ -n "$SSL_KEYFILE" ] \
            && ! as_runtime_user test -r "$SSL_KEYFILE"; then
            mkdir -p /tmp/hoard-tls
            cp "$SSL_CERTFILE" /tmp/hoard-tls/cert.pem
            cp "$SSL_KEYFILE" /tmp/hoard-tls/key.pem
            chown -R "$PUID:$PGID" /tmp/hoard-tls
            chmod 600 /tmp/hoard-tls/key.pem
            export SSL_CERTFILE=/tmp/hoard-tls/cert.pem SSL_KEYFILE=/tmp/hoard-tls/key.pem
        fi
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
