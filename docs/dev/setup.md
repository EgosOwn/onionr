This page assumes that Onionr is already installed and normal user requirements are setup.

The Onionr development environment is simple. All one really needs is a supported Python version (currently 3.7-3.8 as of writing).

There are additional requirements specified in requirements-dev.txt

Intended to be used from VSCode, there are scripts in scripts/ named enable/disable-dev-config.py.
These make modifications to the default config for the purpose of making testing Onionr nodes easier.
Be sure to disable it again before pushing work.

Generally, one should disable bootstrap list usage when making non trivial changes. This is a config option: general.use_bootstrap_list.


