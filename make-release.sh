#!/usr/bin/bash
rm -rf dist
mkdir dist
mkdir dist/onionr/
cp -t dist/onionr/ -r docs static-data install onionr onionr.sh start-daemon.sh setprofile.sh
cp *.md dist/onionr/
PIP_USER=false
export PIP_USER
pip3 install --require-hashes -r requirements.txt --target=dist/onionr/onionr/
pip3 install --require-hashes -r requirements-notifications.txt --target=dist/onionr/onionr/
cd dist
tar -czvf onionr.tar.gz onionr
