#!/bin/sh
if [ -d "/dev/shm" ]
then
    echo "Using /dev/shm to make a RAM based Onionr instance."
else
    echo "This system does not have /dev/shm. Cannot use this script."
    exit 9;
fi
ONIONR_HOME="$(mktemp -p /dev/shm/ -d -t onionr-XXXXXXXXXXX)"
export ONIONR_HOME
echo "Onionr has been launched with a temporary home directory using /dev/shm. Note that the OS may still write to swap if applicable."
echo "Future Onionr commands will use your set or default Onionr home directory, unless you set it to $ONIONR_HOME"
echo "Ultimately, a live boot operating system such as Tails or Debian would be better for you to use."
$(dirname $0)/onionr.sh start & disown
sleep 2
$(dirname $0)/onionr.sh open-home
