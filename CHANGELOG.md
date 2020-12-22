# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [8.0.1] - 2020-12-22

* Fix subprocess in 3.9x with dumb hack
* Dependency bumps

## [8.0.0] - 2020-12-04

* Decrease PoW until better implementation is made


## [7.2.0] - 2020-12-03

* Purge blocks not meeting current pow on startup
* Check block POW before LAN sync
* WSL fixes

## [7.1.0] - 2020-11-23

* Check for ownership of existing dirs in createdirs, this prevents the rare edge case where a user might use a home directory in a location an attacker could write (allowing arbitrary code execution via plugins). This was already partially mitigated by the chmod of the home directory in any case, but this further fixes the issue.

## [7.0.0] - 2020-11-22

* Removed communicator timers
* Removed direct connections and chat (these will be either plugins or separate programs/processes in the future)


## [5.1.0] - 2020-09-07

* Moved plugin web files to be in the plugin folder to reduce staticfiles blueprint coupling
* Added basic sidebar on index page
* Many bug fixes


## [5.0.1] - 2020-08-08

* bumped deadsimplekv to 0.3.2
* bumped urllib3 to 1.25.10

## [5.0.0] - 2020-07-23

- Removed single-process POW support (was only needed on Windows)
