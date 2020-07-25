#!/bin/bash

set -e

cd "$( dirname $0 )"

dest="../bugz/static/bugz/"
mkdir -p "$dest"

yarn install
yarn build

cat \
    build/static/js/runtime*js \
    build/static/js/2*js \
    build/static/js/main*js \
    > "$dest/bundle.js"

mkdir -p "$dest/vendor"

cp -r \
    node_modules/bootstrap/dist/css/bootstrap.min.css \
    node_modules/bootstrap/dist/js/bootstrap.min.js \
    node_modules/jquery/dist/jquery.min.js \
    "$dest/vendor"
