#!/bin/sh
ORIG_ONIONR_RUN_DIR=`pwd`
export ORIG_ONIONR_RUN_DIR
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE="true"
cd "$(dirname "$0")"
cd src
./__init__.py "$@"