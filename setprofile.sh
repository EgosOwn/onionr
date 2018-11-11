#!/bin/bash
ONIONR_HOME=.
if [ $# -gt 0 ]; then
  ONIONR_HOME=$1
export ONIONR_HOME
echo "set ONIONR_HOME to $ONIONR_HOME"
fi
