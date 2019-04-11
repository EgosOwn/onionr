# Onionr HTTP API

# About HTTP API

All HTTP interfaces in the Onionr reference client use the [Flask](http://flask.pocoo.org/) web framework with the [gevent](http://www.gevent.org/) WSGI server.

## Client & Public difference

The client API server is a locked down interface intended for authenticated local communication. 

The public API server is available only remotely from Tor & I2P. It is the interface in which peers use to communicate with one another.

# Client API

Please note: endpoints that simply provide static web app files are not documented here.

(Client API docs coming soon)

# Public API

* /
    - Methods: GET
    - Returns a basic HTML informational banner describing Onionr.
* /getblocklist
    - Methods: GET
    - URI Parameters:
        - date: unix epoch timestamp for offset
    - Returns a list of block hashes stored on the node since an offset (all blocks if no timestamp is specified)
* /getdata/block-hash
    - Methods: GET
    - Returns data for a block based on a provided hash
* /www/file-path
    - Methods: GET
    - Returns file data. Intended for manually sharing file data directly from an Onionr node.
* /ping
    - Methods: GET
    - Returns 'pong!'
* /pex
    - Methods: GET
    - Returns a list of peer addresses reached within recent time
* /announce
    - Methods: POST
    - Accepts form data for 'node' (valid node address) and 'random' which is a nonce when hashed (blake2b_256) in the format `hash(peerAddress+serverAddress+nonce)`, begins with at least 5 zeros.
    - Returns 200 with 'Success' if no error occurs. If the post is invalid, 'failure' with code 406 is returned.
* /upload
    - Methods: POST
    - Accepts form data for 'block' as a 'file' upload.
    - Returns 200 with 'success' if no error occurs. If the block cannot be accepted, 'failure' with 400 is returned.

# Direct Connection API