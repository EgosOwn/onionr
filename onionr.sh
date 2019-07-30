#!/bin/sh
cd "$(dirname "$0")"
cd onionr/
./__init__.py "$@"
