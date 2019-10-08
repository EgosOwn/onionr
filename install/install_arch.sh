#!/bin/bash

EXECUTABLE='/usr/bin/onionr'
OUTPUT_DIR='/usr/share/onionr'
DATA_DIR='/etc/onionr'
LOG_DIR='/var/log/onionr'

BRANCH='master'

# setup error handlers

set -e

trap "echo -e '\033[31mOnionr installation failed.\033[0m' >&2; exit 1337" ERR INT TERM

# require root permissions

if ! [ $(id -u) = 0 ]; then
   echo 'This script must be run as root.' >&2
   exit 1337
fi

# install basic dependencies

echo -e "\033[0;32mInstalling pacman dependencies...\033[0m"

! ((pacman --needed --noconfirm -S git curl python python-pip tor > /dev/null) 2>&1 | grep -v warning 1>&2) | grep .

# get the repository

echo -e "\033[0;32mCloning Onionr repository...\033[0m"

rm -rf "$OUTPUT_DIR" "$DATA_DIR" "$LOG_DIR"

git clone --quiet https://gitlab.com/beardog/onionr "$OUTPUT_DIR" > /dev/null

cd "$OUTPUT_DIR"
git checkout -q "$BRANCH" > /dev/null

# install python dependencies

echo -e "\033[0;32mInstalling pip dependencies...\033[0m"

pip3 install --no-input -r "$OUTPUT_DIR/requirements.txt" --require-hashes > /dev/null

# set permissions on Onionr directory

chmod 755 "$OUTPUT_DIR"
chown -R root:root "$OUTPUT_DIR"

# create directories

mkdir -p "$OUTPUT_DIR/onionr/data" "$LOG_DIR"
mv "$OUTPUT_DIR/onionr/data" "$DATA_DIR"

chmod -R 750 "$DATA_DIR" "$LOG_DIR"
chown -R root:root "$DATA_DIR" "$LOG_DIR"

# create executable

cp "$OUTPUT_DIR/install/onionr" "$EXECUTABLE"

chmod 755 "$EXECUTABLE"
chown root:root "$EXECUTABLE"

# create systemd service

echo -e "\033[0;32mCreating systemd unit...\033[0m"

SERVICE='/etc/systemd/system/onionr.service'

cp "$OUTPUT_DIR/install/onionr.service" "$SERVICE"

chmod 644 "$SERVICE"
chown root:root "$SERVICE"

systemctl daemon-reload
systemctl enable onionr
systemctl start onionr

# pretty header thing

"$EXECUTABLE" details

# and we're good!

trap - ERR

exit 0
