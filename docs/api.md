BLOCK HEADERS (simple ID system to identify block type)
-----------------------------------------------
-crypt- (encrypted block)
-bin- (binary file)
-txt- (plaintext)

HTTP API
------------------------------------------------
/client/ (Private info, not publicly accessible)

-   hello
    - hello world
-   shutdown
    - exit onionr
-   stats
    - show node stats

/public/

-   firstConnect
    - initialize with peer
-   ping
    - pong
-   setHMAC
    - set a created symmetric key 
-   getDBHash
    - get the hash of the current hash database state
-   getPGP
    - export node's PGP public key
-   getData
    - get a data block
-   getBlockHashes
    - get a list of the node's hashes
-------------------------------------------------
