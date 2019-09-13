# Security Policy

We welcome responsible and constructive security review.

# Scope

The Onionr software and any nodes you control are within scope.

Avoid social engineering, volume-based denial of service and disrupting or harming the Onionr network. Do not attempt to exploit any machines/servers you do not own or otherwise have permission to do so.

The following exploits are of particular interest:

* Arbitrary code execution
* API authentication bypass (such as accessing local API from public interface)
* Deanonymization:
  * Easily associating public keys with server addresses
  * Discovering true server IPs when behind Tor/I2P (aside from Tor/i2p-level attacks)
  * Easily discovering which nodes are the block creator
* XSS, CSRF, clickjacking, DNS rebinding
* Timing attacks against the local http server that are exploitable from a browser ([see blog post](https://www.chaoswebs.net/blog/timebleed-breaking-privacy-with-a-simple-timing-attack.html))
* Discovering direct connection servers as a non participant.
* Cryptography/protocol issues
* Denying nodes access to the network by segmenting them out with Sybil nodes

We do not consider non-network based same-machine attacks to be very significant, but we are still willing to listen.

# Rewards

Onionr is a student-owned hobby project, resources are not available for large rewards.

Stickers or other small rewards are available. We reserve the right to refuse rewards for any reason.

Public recognition can be given upon request.

# Contact

Email: beardog [ at ] mailbox.org

PGP (optional): F61A 4DBB 0B3D F172 1F65  0EDF 0D41 4D0F E405 B63B
