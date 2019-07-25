#!/bin/sh

pip3 install --no-input -r "$OUTPUT_DIR/requirements.txt" --require-hashes > /dev/null
