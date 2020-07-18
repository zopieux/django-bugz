#!/bin/bash

set -e

cd "$( dirname $0 )"

dest="../bugz/static/bugz/"
mkdir -p "$dest"

yarn build

cat \
    build/static/js/runtime*js \
    build/static/js/2*js \
    build/static/js/main*js \
    > "$dest/bundle.js"
