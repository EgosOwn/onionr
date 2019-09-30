ONIONR_HOME ?= data
all:;: '$(ONIONR_HOME)'

PREFIX = /usr/local

.DEFAULT_GOAL := setup

setup:
	pip3 install -r requirements.txt --require-hashes --user
	-@cd onionr/static-data/ui/; ./compile.py

install:
	cp -rfp ./onionr $(DESTDIR)$(PREFIX)/share/onionr
	echo '#!/bin/sh' > $(DESTDIR)$(PREFIX)/bin/onionr
	echo 'cd $(DESTDIR)$(PREFIX)/share/onionr' > $(DESTDIR)$(PREFIX)/bin/onionr
	echo './onionr "$$@"' > $(DESTDIR)$(PREFIX)/bin/onionr
	chmod +x $(DESTDIR)$(PREFIX)/bin/onionr

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/share/onionr
	rm -f $(DESTDIR)$(PREFIX)/bin/onionr

test:
	./run_tests.sh

soft-reset:
	@echo "Soft-resetting Onionr..."
	./onionr.sh soft-reset
	@./onionr.sh version | grep -v "Failed" --color=always

reset:
	@echo "Hard-resetting Onionr..."
	rm -rf $(ONIONR_HOME)/ | true > /dev/null 2>&1
	cd onionr/static-data/www/ui/; rm -rf ./dist; python compile.py
	#@./onionr.sh version | grep -v "Failed" --color=always

plugins-reset:
	@echo "Resetting plugins..."
	@./onionr.sh reset-plugins | true > /dev/null 2>&1
	@./onionr.sh version | grep -v "Failed" --color=always
