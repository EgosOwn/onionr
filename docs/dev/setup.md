<h1 align="center">Onionr Developer Guide</h1>

This page assumes that Onionr is already installed and normal user requirements are setup.

The Onionr development environment is simple. All one really needs is a supported Python version (currently 3.7-3.8 as of writing).

There are additional requirements specified in requirements-dev.txt

**Developers agree to the [CoC](../../CODE_OF_CONDUCT.md) and to contribute new code under GPLv3 or later**. Developers should stick to PEP8 in most cases, and write unittests or integration tests where possible.

## Developer Scripts

run-onionr-node.py can be used to start a node with specific parameters

Intended to be used from VSCode (but could work otherwise), there are scripts in scripts/ named enable/disable-dev-config.py.
These make modifications to the default config for the purpose of making testing Onionr nodes easier.
Be sure to disable it again before pushing work.

There are also scripts to generate new tests.

*When adjusting PoW, it will make your node not compatible with the existing network*

Generally, one should disable bootstrap list usage when testing non trivial changes. This is a config option: general.use_bootstrap_list. and can be configured through enable-dev-config.py and run-onionr-node.py


# Current state of Onionr [2021-01-14]

Onionr in it's current form is functional, albeit buggy.


## Current major components

Onionr runs via two main HTTP gevent servers serving Flask apps.

Dir: apiservers

* 1 Parent app hosts all public API endpoints for the Tor transport.
* 1 Parent app hosts all UI-related files and endpoints. Some commands and internal modules interact with this API as well
* The HTTP servers have strict anti-dns-rebinding and CSRF countermeasures, so there is a script to craft requests to the UI-related API in scripts/
* Block storage is currently handled via metadata in sqlite (mostly defunct now), and block data storage in a different database. This is in blocks/ in running Onionr daemon data directory
* cryptography is currently handled in onionrcrypto/ except for ephemeral messages which are handled by onionr
* Transport clients run from looping threads mostly created in communicator/__init__.py, this includes block lookups and uploading on the Tor transport

## Road map

There are several big ways Onionr will be improved in the next major version:

* Migration to the [new modular block system](https://git.voidnet.tech/kev/onionrblocks)
    * Probability proof of work -> verifiable delay function
    * Friend system built on top of signing proofs (Private networks?)
* Gossip transport improvements such as with neighbor improvements. See streamfill/ and [simple gossip](https://github.com/onion-sudo/simplegossip) for incomplete experiments

* Finish removing "communicator"
* I2P transports
    * Gossip
    * Torrents (patch for sha1?)
* Modular transports
    * Currently transports are just threads coupled together.
    * It would be better if there was a generic way to tell any loaded transport what blocks are wanted and feed back received blocks to the database
* Migrate to SafeDB for peers and blocks
    * SafeDB wrapper that contacts http endpoint to store if it is running, otherwise directly open DB
* Separate UI logic from daemon. Refactor code to
* Improve cryptography
    * Restore phrases or deterministic keys (generate key from password, be very careful)
    * Change identities to be dual keys (ed25519+curve25519)
    * Finish treasurechest
        * Interact via [named pipes](https://en.wikipedia.org/wiki/Named_pipe)
        * Ephemeral key management
        * Encrypt/decrypt/sign/verify functions to keep key out of main memory
        * PGP-like symmetric messages


