#!/bin/sh

# change directory to the d3-graphviz blueprint
D3_DIR="/home/dev/src/app/d3-graphviz"
cd "$D3_DIR" || exit

# install and build packages and dependencies for d3-graphviz
yes | yarn install

# make static directory
STATIC_DIR="$D3_DIR/static"
[ -d "$STATIC_DIR" ] || mkdir "$STATIC_DIR"

# define the paths to the d3-graphviz lib files
set -- \
  "$D3_DIR/node_modules/d3/dist/d3.js" \
  "$D3_DIR/node_modules/d3-graphviz/build/d3-graphviz.js" \
  "$D3_DIR/node_modules/d3-graphviz/build/d3-graphviz.js.map" \
  "$D3_DIR/node_modules/@hpcc-js/wasm/dist/graphviz.umd.js" \
  "$D3_DIR/node_modules/@hpcc-js/wasm/dist/graphviz.umd.js.map"

# symbolically link the files to the static directory
for file_path in "$@"; do
  [ -e "$file_path" ] || echo "file does not exist: $file_path"
  static_path="$STATIC_DIR/$(basename "$file_path")"
  [ -L "$static_path" ] || ln -s "$file_path" "$static_path" || echo "failed to create symbolic link: $static_path -> $file_path"
done

# return to the original pwd
cd - || exit
