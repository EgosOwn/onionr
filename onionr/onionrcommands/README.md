# onionrcommands

This module contains handlers/functions for Onionr cli interface commands.

## Files

parser/: Registers and handles Onionr CLI commands

__init__.py: stores the command references (aside from plugins) and help info.

banblocks.py: command handler for manually removing blocks from one's node

daemonlaunch.py: command to run Onionr (start the api servers, tor and communicator)

exportblocks.py: command to export an onionr block to the export folder. Exported blocks can be manually shared outside of the Onionr network

filecommands.py commands to insert and fetch files from the Onionr network

keyadders.py: commands to add an onionr user key or transport address

onionrstatistics.py: commands to print out various information about one's Onionr node

openwebinterface.py: command to open the web interface (useful because it requires a randomly generated token)

plugincommands.py: commands to enable/disable/reload plugins

pubkeymanager.py: commands to generate a new onionr user id, change the active id, or add/remove/list friends

resettor.py: command to delete the Tor data directory