#!/bin/sh

# install d3-graphviz
./home/dev/src/app/d3-graphviz/install.sh

if [ -z "$DEVCONTAINER" ]; then
    echo "[FoxConnect] starting production server"
    hypercorn "$APP_FACTORY()" --bind "$APP_HOST:$APP_PORT"
fi

exec "$@"
