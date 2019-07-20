#!/bin/sh

make plugins-reset
find . -name '__pycache__' -type d | xargs rm -rf
