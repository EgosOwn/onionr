# onionrusers

onionrusers is a small collection of classes for interacting with onionr public keys, such as encrypting messages to them with forward secrecy, interacting with their settings, or else.

## Files

onionrusers.py: OnionrUsers class can be used to encrypt/decrypt messages to a particular Onionr user (incl. forward secrecy), view information about them, and get our friend list.

contactmanager.py: Inheriting from OnionrUsers, ContactManager allows arbitrary information to be associated with an Onionr user.