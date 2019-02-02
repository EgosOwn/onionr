#!/usr/bin/bash
cd "$(dirname "$0")"
echo "starting Onionr daemon..."
echo "run onionr.sh stop to stop the daemon, or onionr.sh start to get output"
nohup ./onionr.sh start & disown > /dev/null
