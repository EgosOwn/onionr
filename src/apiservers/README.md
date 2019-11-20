# API Servers

Contains the WSGI servers Onionr uses for remote peer communication and local daemon control

## Files

* \_\_init\_\_.py: Exposes the server classes
* private: Contains the client API (the server used to interact with the local Onionr daemon, and view the web UI)
* public: Contains the public API (the server used by remote peers to talk to our daemon)