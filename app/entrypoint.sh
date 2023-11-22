#!/bin/sh

# install d3-graphviz
./home/dev/src/app/d3-graphviz/install.sh

if [ -z "$DEVCONTAINER" ]; then
    echo "[FoxConnect] starting production server"
    waitress-serve --host="$APP_HOST" --port="$APP_PORT" --call "$APP_OBJECT"
fi

exec "$@"
