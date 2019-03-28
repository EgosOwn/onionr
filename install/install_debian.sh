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

apt -y install git curl python3.7 python3-pip python3-setuptools tor

# get the repository

rm -rf "$OUTPUT_DIR" "$DATA_DIR" "$LOG_DIR"

git clone https://gitlab.com/beardog/onionr "$OUTPUT_DIR"

cd "$OUTPUT_DIR"
git checkout "$BRANCH"

# install python dependencies

python3.7 -m pip install --no-input -r "$OUTPUT_DIR/requirements.txt" --require-hashes

# create nologin onionr user if not exists

id -u onionr &>/dev/null || useradd -r -s /sbin/nologin onionr

chmod 755 "$OUTPUT_DIR"
chown -R onionr:onionr "$OUTPUT_DIR"

# create directories

mkdir -p "$OUTPUT_DIR/onionr/data" "$LOG_DIR"
mv "$OUTPUT_DIR/onionr/data" "$DATA_DIR"

chmod -R 750 "$DATA_DIR" "$LOG_DIR"
chown -R onionr:onionr "$DATA_DIR" "$LOG_DIR"

# create executable

cp "$OUTPUT_DIR/install/onionr" "$EXECUTABLE"

chmod 755 "$EXECUTABLE"
chown root:root "$EXECUTABLE"

# create systemd service

SERVICE='/etc/systemd/system/onionr.service'

cp "$OUTPUT_DIR/install/onionr.service" "$SERVICE"

chmod 644 "$SERVICE"
chown root:root "$SERVICE"

systemctl daemon-reload
systemctl enable onionr
systemctl start onionr

# pretty header thing

"$EXECUTABLE" --header 'Onionr successfully installed.'

# and we're good!

trap - ERR

exit 0
