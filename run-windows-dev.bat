@echo off
echo This script is only intended for use in Onionr development, as it uses a random profile.
set ONIONR_HOME=data%random%
echo Using profile: %ONIONR_HOME%
setlocal
chdir src
python __init__.py %*
