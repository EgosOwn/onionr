<p align="center">

<img src="./docs/onionr-logo.png">

</p>

(***pre-alpha quality & experimental, not well tested or easy to use yet***)

[![Open Source Love](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)


Anonymous P2P platform, using Tor & I2P.

<hr>

**The main repository for this software is at https://gitlab.com/beardog/Onionr/**

# Summary

Onionr is a decentralized, peer-to-peer data storage network, designed to be anonymous and resistant to (meta)data analysis and spam.

Onionr stores data in independent packages referred to as 'blocks' (not to be confused with a blockchain). The blocks are synced to all other nodes in the network. Blocks and user IDs cannot be easily proven to have been created by particular nodes (only inferred).

Users are identified by ed25519 public keys, which can be used to sign blocks (optional) or send encrypted data.

Onionr can be used for mail, as a social network, instant messenger, file sharing software, or for encrypted group discussion.


## Main Features

* [X] Fully p2p/decentralized, no trackers or other single points of failure
* [X] End to end encryption of user data
* [X] Optional non-encrypted blocks, useful for blog posts or public file sharing
* [X] Easy API system for integration to websites
* [X] Metadata analysis resistance

**Onionr API and functionality is subject to non-backwards compatible change during pre-alpha development**

# Install and Run on Linux

The following applies to Ubuntu Bionic. Other distros may have different package or command names.

* Have python3.5+, python3-pip, Tor (daemon, not browser) installed (python3-dev recommended)
* Clone the git repo: `$ git clone https://gitlab.com/beardog/onionr`
* cd into install direction: `$ cd onionr/`
* Install the Python dependencies ([virtualenv strongly recommended](https://virtualenv.pypa.io/en/stable/userguide/)): `$ pip3 install -r requirements.txt`

## Help out

Everyone is welcome to help out. Help is wanted for the following:

* Development (Get in touch first)
    * Creation of a shared object library for use from other languages and faster proof-of-work
    * Onionr mobile app development
    * Windows and Mac support
    * General development
* Testing
* Running stable nodes
* Security review/audit

Bitcoin/Bitcoin Cash: 1onion55FXzm6h8KQw3zFw2igpHcV7LPq

## Disclaimer

The Tor Project, I2P developers, and anyone else do not own, create, or endorse this project, and are not otherwise involved.

The badges (besides travis-ci build) are by Maik Ellerbrock is licensed under a Creative Commons Attribution 4.0 International License.