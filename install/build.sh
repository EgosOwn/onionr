#!/bin/sh

sudo pip3 install -r requirements.txt
make plugins-reset
find . -name '__pycache__' -type d | xargs rm -rf
