.DEFAULT_GOAL := setup

setup:
	sudo pip3 install -r requirements.txt
	sudo rm -rf /usr/share/onionr/
	sudo rm -f /usr/bin/onionr

install:
	sudo cp -rp ./onionr /usr/share/onionr
	sudo sh -c "echo \"#!/bin/sh\ncd /usr/share/onionr/\n./onionr.py \\\"\\\$$@\\\"\" > /usr/bin/onionr"
	sudo chmod +x /usr/bin/onionr
	sudo chown -R `whoami` /usr/share/onionr/

uninstall:
	sudo rm -rf /usr/share/onionr
	sudo rm -f /usr/bin/onionr

test:
	@cd onionr; ./tests.py
	
reset:
	echo "RESETING ONIONR"
	rm -f onionr/data/blocks/*.dat | true > /dev/null 2>&1
	rm -f onionr/data/peers.db | true > /dev/null 2>&1
	rm -f onionr/data/blocks.db | true > /dev/null 2>&1

