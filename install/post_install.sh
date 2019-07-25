#!/bin/sh

systemctl daemon-reload
systemctl enable onionr
systemctl start onionr
