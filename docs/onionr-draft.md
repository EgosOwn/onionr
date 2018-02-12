# Onionr Protocol Spec

A social network/microblogging platform for Tor & I2P

Draft Dec 25 2017

# Overview

Onionr is an encrypted microblogging & mailing system designed in the spirit of Twitter.
There are no central servers and all traffic is peer to peer by default (routed via Tor or I2P).
User IDs are simply Tor onion service/I2P host id + PGP fingerprint.
Clients consolidate feeds from peers into 1 “timeline” using RSS format.
Private messages are only accessible by the intended peer based on the PGP id.
Onionr is not intended to be a replacement for Ricochet, OnionShare, or Briar.
All traffic is over onion/I2P because if only some was, then that would make that traffic inherently suspicious.
## Goals:
    • Selective sharing of information with friends & public
    • Secure & semi-anonymous direct messaging
    • Forward secrecy
    • Defense in depth
    • Data should be secure for years to come, quantum safe (though not necessarily every “layer”)
    • Decentralization
    * Avoid browser-based exploits that plague similar software
    * Avoid timing attacks & unexpected metadata leaks
## Assumptions:
    • Tor & I2P’s transport protocols & AES-256 are not broken, sha3-512 2nd preimage attacks will remain infeasible indefinitely
    • All traffic is logged indefinitely by powerful adversaries
## Protocol
Clients MUST use HTTP(s) to communicate with one another to maintain compatibility cross platform. HTTPS is recommended, but HTTP is acceptable because Tor & I2P provide transport layer security.
## Connections
    When a node first comes online, it attempts to bootstrap using a default list provided by a client.
    When two peers connect, they exchange PGP public keys and then generate a shared AES-SHA3-512 HMAC token. These keys are stored in a peer database until expiry.
    HMAC tokens are regenerated either every X many communications with a peer or every X minutes. Every 10MB or every 2 hours is a recommended default.
    All valid requests with HMAC should be recorded until used HMAC's expiry to prevent replay attacks.
    Peer Types
        * Friends:
            * Encrypted ‘friends only’ posts to one another
            * Usually less strict rate & storage limits
            * OPTIONALLY sign one another’s keys. Users may not want to do this in order to avoid exposing their entire friends list.
        • Strangers:
            * Used for storage of encrypted or public information
            * Can only read public posts
            * Usually stricter rate & storage limits
## Data Storage/Delivery

    Posts (public or friends only) are stored across the network.
    Private messages SHOULD be delivered directly if both peers are online, otherwise stored in the network.
    Data SHOULD be stored in an entirely encrypted state when a client is offline, including metadata. Data SHOULD be stored in a minimal size with garbage data to ensure some level of plausible deniablity.
    Data SHOULD be stored as long as the node’s user prefers and only erased once disk quota is reached due to new data.
    Posts
    Posts can contain text and images. All posts MUST be time stamped.
    Images SHOULD not be displayed by non-friends by default, to prevent unwanted viewing of offensive material & to reduce attack surface.
    All received posts must be verified to be stored and/or displayed to the user.

    All data being transfered MUST be encrypted to the end node receiving the data, then the data MUST be encrypted the node(s) transporting/storing the data,

     Posts have two settings:
        • Friends only:
            ◦ Posts MUST be encrypted to all trusted peers via AES256-HMAC-SHA256 and PGP signed (signed before encryption) and time stamped to prevent replaying. A temporary RSA key for use in every post (or message) is exchanged every X many configured post (or message), for use in addition with PGP and the HMAC.
        • Public:
            ◦ Posts MUST be PGP signed, and MUST NOT use any encryption.
## Private Messages

    Private messages are messages that can have attached images. They MUST be encrypted via AES256-HMAC-SHA256 and PGP signed (signed before encryption) and time stamped to prevent replaying. A temporary EdDSA key for use in every message is exchanged every X many configured messages (or posts), for use in addition with PGP and the HMAC.
    When both peers are online messages SHOULD be dispatched directly between peers.
    All messages must be verified prior to being displayed.

    Clients SHOULD allow configurable message padding.
## Spam mitigation

To send or receive data, a node can optionally request that the other node generate a hash that when in hexadecimal representation contains a random string at a random location in the string. Clients will configure what difficulty to request, and what difficulty is acceptable for themselves to perform. Difficulty should correlate with recent network & disk usage and data size. Friends can be configured to have less strict (to non existent) limits, separately from strangers. (proof of work).
Rate limits can be strict, as Onionr is not intended to be an instant messaging application.
