# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

* Made storagecounter use a watchdog (inotify) instead of excessive file reads
* Bumped urllib3 to 1.25.10
* Removed use of communicator's storagecounter to reduce coupling

## [5.0.0] - 2020-07-23

- Removed single-process POW support (was only needed on Windows)

