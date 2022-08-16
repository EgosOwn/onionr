# Onionr Roadmap


## Taraxacum Release (9.0)


* [ X ] Implement new block format with verifiable delay function

* [ X ] Implement overhauled gossip system with dandelion++

    The new system is separated from the underlying networks used and makes it much easier to implement new transport methods. Dandelion++ is also better than the old block mixing we did.


## Misc

* [  ] Spruce up documentation
* [  ] Restore LAN transport
* [  ] Restore webUI as a plugin
* [  ] Restore static site/file sharing plugin
* [  ] Restore/reimplement mail plugin
* [  ] Restore/reimplement friends plugin
* [  ] Refresh test suite
* [  ] Revamped key/encrypted messaging (encrypted blocks)



## Web of trust release (~10.0)

To facilitate the below market plugin/application, Onionr will need a web of trust system.

* [ ] Web of trust plugin or module


## Market Plugin Release (~10.1)

The Onionr team believes the Monero community is currently lacking a good p2p market, and as such we hope to build a solution using Onionr as a transport. This may be a separate project and as opposed to a plugin.


* A new marketplace plugin will be developed with the following *tenative* features:

* [ ] Account management
* [ ] Monero management
* [ ] Store front discovery and search
* [ ] Product listing search
* [ ] User reviews

