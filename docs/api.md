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
-------------------------------------------------
