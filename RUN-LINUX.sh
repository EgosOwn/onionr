#!/bin/sh
cd onionr/
cp -R static-data/default-plugins/pms/ data/plugins/
cp -R static-data/default-plugins/flow/ data/plugins/
./onionr.py "$@"
