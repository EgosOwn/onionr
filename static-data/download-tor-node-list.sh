#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
curl https://www.dan.me.uk/torlist/ > tor-node-list.dat
sed -i 's|^#.*$||g' tor-node-list.dat
