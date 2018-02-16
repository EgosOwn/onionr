# Onionr Protocol Spec v2

A P2P platform for Tor & I2P

# Overview

Onionr is an encrypted microblogging & mailing system designed in the spirit of Twitter.
There are no central servers and all traffic is peer to peer by default (routed via Tor or I2P).
User IDs are simply Tor onion service/I2P host id + Ed25519 key fingerprint.
Private blocks are only able to be read by the intended peer.
All traffic is over Tor/I2P, connecting only to Tor onion and I2P hidden services.

## Goals:
    • Selective sharing of information
    • Secure & semi-anonymous direct messaging
    • Forward secrecy
    • Defense in depth
    • Data should be secure for years to come
    • Decentralization
    * Avoid browser-based exploits that plague similar software
    * Avoid timing attacks & unexpected metadata leaks

## Protocol

Onionr nodes use HTTP (over Tor/I2P) to exchange keys, metadata, and blocks. Blocks are identified by their sha3_256 hash. Nodes sync a table of blocks hashes and attempt to download blocks they do not yet have from random peers.

## Connections

When a node first comes online, it attempts to bootstrap using a default list provided by a client.
When two peers connect, they exchange Ed25519 keys (if applicable) then Salsa20 keys.

Salsa20 keys are regenerated either every X many communications with a peer or every X minutes. 

Every 100kb or every 2 hours is a recommended default.

All valid requests with HMAC should be recorded until used HMAC's expiry to prevent replay attacks.
Peer Types
    * Friends:
        * Encrypted ‘friends only’ posts to one another
        * Usually less strict rate & storage limits
    * Strangers:
        * Used for storage of encrypted or public information
        * Can only read public posts
        * Usually stricter rate & storage limits

## Spam mitigation

To send or receive data, a node can optionally request that the other node generate a hash that when in hexadecimal representation contains a random string at a random location in the string. Clients will configure what difficulty to request, and what difficulty is acceptable for themselves to perform. Difficulty should correlate with recent network & disk usage and data size. Friends can be configured to have less strict (to non existent) limits, separately from strangers. (proof of work).
Rate limits can be strict, as Onionr is not intended to be an instant messaging application.