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

## Blocks

Onionr blocks are very simple. They are structured in two main parts: a metadata section and a data section, with a line feed delimiting where metadata ends and data begins. Metadata defines what kind of data is in a block, signature data, encryption settings, and other arbitrary information.

For encryption, Onionr uses ephemeral Curve25519 keys for key exchange and XSalsa20-Poly1305 as a symmetric cipher, or optionally using only XSalsa20-Poly1305.


