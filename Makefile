.DEFAULT_GOAL := setup

setup:
	sudo pip3 install -r requirements.txt

install:
	sudo rm -rf /usr/share/onionr/
	sudo rm -f /usr/bin/onionr
	sudo cp -rp ./onionr /usr/share/onionr
	sudo sh -c "echo \"#!/bin/sh\ncd /usr/share/onionr/\n./onionr.py \\\"\\\$$@\\\"\" > /usr/bin/onionr"
	sudo chmod +x /usr/bin/onionr
	sudo chown -R `whoami` /usr/share/onionr/

uninstall:
	sudo rm -rf /usr/share/onionr
	sudo rm -f /usr/bin/onionr

test:
	@rm -rf onionr/data-backup
	@mv onionr/data onionr/data-backup | true > /dev/null 2>&1
	-@cd onionr; ./tests.py
	@rm -rf onionr/data
	@mv onionr/data-backup onionr/data | true > /dev/null 2>&1

reset:
	rm -f onionr/data/blocks/*.dat | true > /dev/null 2>&1
	rm -f onionr/data/peers.db | true > /dev/null 2>&1
	rm -f onionr/data/blocks.db | true > /dev/null 2>&1
	rm -f onionr/data/address.db | true > /dev/null 2>&1
