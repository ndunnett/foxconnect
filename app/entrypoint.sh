#!/bin/sh

if [ -z "$DEVCONTAINER" ]; then
    echo "[FoxConnect] starting production server"
    waitress-serve --host="$APP_HOST" --port="$APP_PORT" "$APP_OBJECT"
fi

exec "$@"
