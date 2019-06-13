# communicatorutils

The files in this submodule handle various subtasks and utilities for the onionr communicator.

## Files:

announcenode.py: Uses a communicator instance to announce our transport address to connected nodes

connectnewpeers.py: takes a communicator instance and has it connect to as many peers as needed, and/or to a new specified peer.

cooldownpeer.py: randomly selects a connected peer in a communicator and disconnects them for the purpose of security and network balancing.

daemonqueuehandler.py: checks for new commands in the daemon queue and processes them accordingly.

deniableinserts.py: insert fake blocks with the communicator for plausible deniability

downloadblocks.py: iterates a communicator instance's block download queue and attempts to download the blocks from online peers

housekeeping.py: cleans old blocks and forward secrecy keys

lookupadders.py: ask connected peers to share their list of peer transport addresses

lookupblocks.py: lookup new blocks from connected peers from the communicator

netcheck.py: check if the node is online based on communicator status and onion server ping results

onionrcommunicataortimers.py: create a timer for a function to be launched on an interval. Control how many possible instances of a timer may be running a function at once and control if the timer should be ran in a thread or not.

proxypicker.py: returns a string name for the appropriate proxy to be used with a particular peer transport address.

servicecreator.py: iterate connection blocks and create new direct connection servers for them.

uploadblocks.py: iterate a communicator's upload queue and upload the blocks to connected peers