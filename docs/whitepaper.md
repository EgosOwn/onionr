<p align="center">
   <h1 align="center">Onionr</h1>
</p>

<p align="center">Anonymous, Decentralized, Distributed Network</p>

June 2020

# Introduction

We believe that the ability to communicate freely with others is crucial for maintaining societal and personal liberty. The internet has provided humanity with the ability to spread information globally, but there are many persons and organizations who try to stifle the flow of information, sometimes with success.

Internet censorship comes in many forms, state censorship, threats of violence, network exploitation (e.g. denial of service attacks) and others.

We hold that in order to protect individual privacy, users must have the ability to communicate anonymously and with decentralization.

We believe that in order to prevent censorship and loss of information, these measures must be in place:

* Resistance to censorship of underlying infrastructure or of particular network hosts

* Anonymization of users by default
   * The Inability to coerce users (personal threats/"doxxing", or totalitarian regime censorship)

* Economic availability. A system should not rely on a single device to be constantly online, and should not be overly expensive to use. The majority of people in the world own cell phones, but comparatively few own personal computers, particularly in developing countries. Internet connectivity can be slow or spotty in many areas.

# Onionr Design Goals

When designing Onionr we had these main goals in mind:

* Anonymous Blocks
   * Difficult to determine block creator or users regardless of transport used
* Node-anonymity
* Transport agnosticism
* Default global sync, but configurable
* Spam resistance

# Onionr Design

(See the spec for specific details)

## General Overview

At its core, Onionr is merely a description for storing data in self-verifying packages ("blocks"). These blocks can be encrypted to a user (or for one's self), encrypted symmetrically, or not at all. Blocks can be signed by their creator, but regardless, they are self-verifying due to being identified by a sha3-256 hash value; once a block is created, it cannot be modified.

Onionr exchanges a list of blocks between all nodes. By default, all nodes download and share all other blocks, however, this is configurable. Blocks do not rely on any particular order of receipt or transport mechanism.

## User IDs

User IDs are simply Ed25519 public keys. They are represented in Base32 format or encoded using the [PGP Word List](https://en.wikipedia.org/wiki/PGP_word_list).

Public keys can be generated deterministically with a password using a key derivation function (Argon2id). This password can be shared between many users in order to share data anonymously among a group, using only 1 password. This is useful in some cases, but is risky, as if one user causes the key to be compromised and does not notify the group or revoke the key, there is no way to know.

## Nodes

Although Onionr is transport agnostic, the only supported transports in the reference implementation are Tor .onion services and I2P hidden services. Nodes announce their address on creation by connecting to peers specified in a bootstrap file. Peers in the bootstrap file have no special permissions aside from being default peers.

### Node Profiling

To mitigate maliciously slow or unreliable nodes, Onionr builds a profile on nodes it connects to. Nodes are assigned a score, which raises based on the number of successful block transfers, speed, and reliability of a node, and reduces the score based on how unreliable a node is. If a node is unreachable for over 24 hours after contact, it is forgotten. Onionr can also prioritize connections to 'friend' nodes.

## Block Format

Onionr blocks are very simple. They are structured in two main parts: a metadata section and a data section, with a line feed delimiting where metadata ends and data begins.

Metadata defines what kind of data is in a block, signature data, encryption settings, and other arbitrary information.

Optionally, a random token can be inserted into the metadata for use in Proof of Work.

The proof of work function should be a Verifiable Delay Function (VDF). We have chosen MiMC for it's simplicity.

### Block Encryption

For encryption, Onionr uses ephemeral Curve25519 keys for key exchange and XSalsa20-Poly1305 as a symmetric cipher or optionally using only XSalsa20-Poly1305 with a pre-shared key.

Regardless of encryption, blocks can be signed internally using Ed25519.

## Block Exchange

Blocks can be exchanged using any method, as they are not reliant on any other blocks.

By default, every node shares a list of the blocks it is sharing, and will download any blocks it does not yet have.

## Spam mitigation and block storage time

By default, an Onionr node adjusts the target difficulty for blocks to be accepted based on the percent of disk usage allocated to Onionr.

Blocks are stored indefinitely until the allocated space is filled, at which point Onionr will remove the oldest blocks as needed, save for "pinned" blocks, which are permanently stored.

## Block Timestamping

Onionr blocks are by default not accepted if their timestamp is set too far in the past, or is in the future.

In addition, randomness beacons such as the one operated by [NIST](https://beacon.nist.gov/home), [Chile](https://beacon.clcert.cl/), or the hash of the latest blocks in a cryptocurrency network could be used to affirm that a block was at least not *created* before a given time.

# Direct Connections

We propose a method of using Onionr's block sync system to enable direct connections between peers by having one peer request to connect to another using the peer's public key. Since the request is within a standard block, proof of work must be used to request a connection. If the requested peer is available and wishes to accept the connection, Onionr will generate a temporary .onion address for the other peer to connect to. Alternatively, a reverse connection may be formed, which is faster to establish but requires a message brokering system instead of a standard socket.

The benefits of such a system are increased privacy, and the ability to anonymously communicate from multiple devices at once. In a traditional onion service, one's online status can be monitored and more easily correlated.

# Threat Model

The goal of Onionr is to provide a method of distributing information in a manner in which the difficulty of discovering the identity of those sending and receiving the information is greatly increased. In this section we detail what information we want to protect and who we're protecting it from.

In this threat model, "protected" means available in plaintext only to those which it was intended, and regardless non-malleable

## Threat Actors

Onionr assumes that traffic/data is being surveilled by powerful actors on every level but the user's device.

We also assume that the actors are capable of the following:

* Running tens of thousands of Onionr nodes
* Surveiling most of the Tor and I2P networks

## Protected Data

We seek to protect the following information:

* Contents of private data. E.g. 'mail' messages and secret files
* Relationship metadata. Unless something is desired to be published publicly, we seek to hide the creator and recipients of such data.
* Physical location/IP address of nodes on the network
* All block data from tampering

### Unprotected Data

Onionr does not protect the following:

* Data specifically inserted as plaintext is available to the public
* The public key of signed plaintext blocks
* The fact that one is using Tor or I2P
   * The fact that one is using Onionr specifically can likely be discovered using long term traffic analysis
   * Intense traffic analysis may be able to discover what node created a block. For this reason we offer a high security setting to only share blocks via uploads that we recommend for those who need the best privacy.

## Assumptions

We assume that Tor onion services (v3) and I2P services cannot be trivially deanonymized, and that the underlying cryptographic primitives we employ cannot be broken in any manner faster than brute force unless a quantum computer is used.

Once quantum safe algorithms are more mature and have decent high level libraries, they will be deployed.

# Conclusion

If successful, Onionr will be a complete decentralized platform for anonymous computing, complete with limited metadata exposure, both node and user anonymity, and spam prevention
