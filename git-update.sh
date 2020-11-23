#!/bin/bash

echo "This will git pull origin master, then update dependencies and default plugins."
echo "Enter to continue, ctrl-c to stop."
read

git pull origin master
pip install -r --require-hashes requirements.txt
./onionr.sh reset-plugins
