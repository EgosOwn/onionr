@echo off
set ONIONR_HOME=data%random%
echo Using %ONIONR_HOME%
setlocal
chdir onionr
python onionr.py %*
