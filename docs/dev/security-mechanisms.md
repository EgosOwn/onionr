# Onionr Security Mechanisms


## bigbrother 👁️

Bigbrother is a cheeky module that uses Python3.8+ sys auditing events to log and/or block certain sensitive events.

It has a little overhead, so one can disable it in config in general.security_auditing

[ChaosWebs.net/blog/preventing-arbitrary-code-execution-in-python38-with-auditing.html](https://chaoswebs.net/blog/preventing-arbitrary-code-execution-in-python38-with-auditing.html)

### Threat model

It is intended to log bugs leaking private file system information, block+log network leaks, and block+log eval-like arbitrary code execution. It is not intended to block malicious browser scripts or malicious Python plugins. It cannot work with subprocesses that do not activate the module.

It's not intended to be bulletproof by any means, but it helps.

### What big brother does

* Disk access checks for disk access outside. Only logs, does not block
* Network leaks. (Non Tor/LAN) Blocks and logs
* Arbitrary code execution: logs and blocks non-whitelisted bytecode importing/compiling and subprocesses.


## Sybil attacks

As with any decentralized network, sybil nodes could collude to spy or cause mayhem. Due to the gossip nature of Onionr, sybil nodes would have a hard time fully stopping the network. In terms of spying, they could not conclusively prove the origin of messages due to the multiple transport nature of the network and layering behind Tor/etc.

## Tor configuration

When managed by Onionr, Tor has a control port password that gets stored in Onionr config.

Tor is also configured to reject requests to non-onion services, which helps to stop redirect based denial of service attacks.

## Web security

Onionr secures both it's main web APIs with anti-dns-rebinding logic, which validates the host header used in connections to it. This is to prevent exfiltration of data and side channel deanonymization.

Onionr secures the client API with a token that must be passed in most requests, with the exception of static API files. This is to prevent CSRF and side channel deanonymization.

Onionr binds most services to random loopback addresses to reduce all cross-site web attacks, including discovery of Onionr on a computer from a normal website. This is not supported on Mac because Mac does not support non 'typical' loopback addresses.

Onionr has a strict content-security-policy, rejecting all non-localhost requests and denying inline scripts and similar insecure sources.
