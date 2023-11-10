#!/bin/sh

if [ -z "$DEVCONTAINER" ]; then
    echo "[FoxConnect] starting production server"
    waitress-serve --host="$APP_HOST" --port="$APP_PORT" --call "$APP_OBJECT"
fi

exec "$@"
