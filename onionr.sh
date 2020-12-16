#!/bin/sh
ORIG_ONIONR_RUN_DIR=`pwd`
export ORIG_ONIONR_RUN_DIR
cd "$(dirname "$0")"
cd src
./__init__.py "$@"