#!/bin/sh
ORIG_ONIONR_RUN_DIR=`pwd`
cd "$(dirname "$0")"
cd onionr
./__init__.py "$@"
