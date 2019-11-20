# Onionr Communicator

Onionr communicator is the Onionr client. It "connects" to remote Onionr peers and does things such as:

* Finding new peers
* Uploading blocks
* Downloading blocks
* Daemon maintenance/housekeeping

## Files

* \_\_init\_\_.py: Contains the main communicator code. Inits and launches the communicator and sets up the timers
* peeraction.py: contains a function to send commands to remote peers
* bootstrappers.py: adds peers from the bootstrap list to the communicator to try to connect to them
* onlinepeers: management of the online peer pool for the communicator