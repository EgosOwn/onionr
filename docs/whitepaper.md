<p align="center">
 <img src="onionr-logo.png" alt="<h1>Onionr</h1>">
</p>
<p align="center">Anonymous, Decentralized, Distributed Network</p>

# Introduction

The most important thing in the modern world is information. The ability to communicate freely with others. The internet has provided humanity with the ability to spread information globally, but there are many people who try (and sometimes succeed) to stifle the flow of information.

Internet censorship comes in many forms, state censorship, corporate consolidation of media, threats of violence, network exploitation (e.g. denial of service attacks).

To prevent censorship or loss of information, these measures must be in place:

* Resistance to censorship of underlying infrastructure or of network hosts

* Anonymization of users by default
   * The Inability to violently coerce human users (personal threats/"doxxing", or totalitarian regime censorship)

* Economic availability. A system should not rely on a single device to be constantly online, and should not be overtly expensive to use. The majority of people in the world own cell phones, but comparatively few own personal computers, particularly in developing countries.

There are many great projects that tackle decentralization and privacy issues, but there are none which tackle all of the above issue. Some of the existing networks have also not worked well in practice, or are more complicated than they need to be.

# Onionr Design Goals

When designing Onionr we had these goals in mind:

* Anonymous Blocks

 * Difficult to determine block creator or users regardless of transport used
* Default Anonymous Transport Layer
 * Tor and I2P
* Transport agnosticism
* Default global sync, but can configure what blocks to seed
* Spam resistance
* Encrypted blocks

# Onionr Design

(See the spec for specific details)

## General Overview

At its core, Onionr is merely a description for storing data in self-verifying packages ("blocks"). These blocks can be encrypted to a user (or self), encrypted symmetrically, or not at all. Blocks can be signed by their creator, but regardless, they are self-verifying due to being identified by a sha3-256 hash value; once a block is created, it cannot be modified.

Onionr exchanges a list of blocks between all nodes. By default, all nodes download and share all other blocks, however this is configurable.

## User IDs

User IDs are simply Ed25519 public keys. They are represented in Base32 format, or encoded using the [PGP Word List](https://en.wikipedia.org/wiki/PGP_word_list).

Public keys can be generated deterministicly with a password using a key derivation function (Argon2id). This password can be shared between many users in order to share data anonymously among a group, using only 1 password. This is useful in some cases, but is risky, as if one user causes the key to be compromised and does not notify the group or revoke the key, there is no way to know.

## Nodes

Although Onionr is transport agnostic, the only supported transports in the reference implemetation are Tor .onion services and I2P hidden services. Nodes announce their address on creation.

### Node Profiling

To mitigate maliciously slow or unreliable nodes, Onionr builds a profile on nodes it connects to. Nodes are assigned a score, which raises based on the amount of successful block transfers, speed, and reliabilty of a node, and reduces based on how unreliable a node is. If a node is unreachable for over 24 hours after contact, it is forgotten. Onionr can also prioritize connection to 'friend' nodes.

## Block Format

Onionr blocks are very simple. They are structured in two main parts: a metadata section and a data section, with a line feed delimiting where metadata ends and data begins. 

Metadata defines what kind of data is in a block, signature data, encryption settings, and other arbitrary information.

Optionally, a random token can be inserted into the metadata for use in Proof of Work.

### Block Encryption

For encryption, Onionr uses ephemeral Curve25519 keys for key exchange and XSalsa20-Poly1305 as a symmetric cipher, or optionally using only XSalsa20-Poly1305 with a pre-shared key.

Regardless of encryption, blocks can be signed internally using Ed25519.

## Block Exchange

Blocks can be exchanged using any method, as they are not reliant on any other blocks.

By default, every node shares a list of the blocks it is sharing, and will download any blocks it does not yet have.

## Spam mitigation and block storage time

By default, an Onionr node adjusts the target difficulty for blocks to be accepted based on the percent of disk usage allocated to Onionr.

Blocks are stored indefinitely until the allocated space is filled, at which point Onionr will remove the oldest blocks as needed, save for "pinned" blocks, which are permanently stored.

## Block Timestamping

Onionr can provide evidence when a block was inserted by requesting other users to sign a hash of the current time with the block data hash: sha3_256(time + sha3_256(block data)).

This can be done either by the creator of the block prior to generation, or by any node after insertion.