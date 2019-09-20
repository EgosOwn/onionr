#!/bin/bash
cd "$(dirname "$0")"
echo "starting Onionr daemon..."
echo "run onionr.sh stop to stop the daemon"
touch daemon-true.txt
exec nohup ./onionr.sh start > /dev/null 2>&1 & disown
