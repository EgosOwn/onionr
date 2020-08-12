# Onionr Installation

The following steps work broadly speaking for WSL, Mac, and Linux.

1. Verify python3.7+ is installed: if not, see https://www.python.org/downloads/

2. Verify Tor is installed (does not need to be running, binary can be put into system path or Onionr directory)

3. [Optional but recommended]: setup virtual environment using [virtualenv](https://virtualenv.pypa.io/en/latest/), activate the virtual environment

4. Clone Onionr: `$ git clone https://gitlab.com/beardog/onionr`

5. Install the Python module dependencies: `$ pip3 install --require-hashes -r requirements.txt`


Note: if an alternative python install is needed, use virtualenv or run Onionr commands with:

`$ /path/to/python /path/to/onionr/onionr/__init__.py`