# onionrservices

onionservices is a submodule to handle direct connections to Onionr peers, using the Onionr network to broker them.

## Files

__init__.py: Contains the OnionrServices class which can create direct connection servers or clients.

bootstrapservice.py: Creates a bootstrap server for a peer and announces the connection by creating a block encrypted to the peer we want to connect to.

connectionserver.py: Creates a direct connection server for a peer

httpheaders.py: Modifies a Flask response object http response headers for security purposes.