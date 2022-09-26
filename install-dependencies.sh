#!/bin/bash

# install base dependencies
pip install -r requirements.txt --user --require-hashes

# iterate plugin directories for their dependencies

for d in static-data/default-plugins/*; do
    if [ -d "$d" ]; then
        echo "Installing dependencies for $d"
        pip install -r $d/requirements.txt --user --require-hashes
    fi
done
