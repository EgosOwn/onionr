# communicatorutils

The files in this submodule handle various subtasks and utilities for the onionr communicator.

## Files:

connectnewpeers.py: takes a communicator instance and has it connect to as many peers as needed, and/or to a new specified peer.

daemonqueuehandler.py: checks for new commands in the daemon queue and processes them accordingly.

downloadblocks.py: iterates a communicator instance's block download queue and attempts to download the blocks from online peers

lookupadders.py: ask connected peers to share their list of peer transport addresses

onionrcommunicataortimers.py: create a timer for a function to be launched on an interval. Control how many possible instances of a timer may be running a function at once and control if the timer should be ran in a thread or not.

onionrdaemontools.py: contains the DaemonTools class which has a lot of etc functions useful for the communicator. Deprecated.

proxypicker.py: returns a string name for the appropriate proxy to be used with a particular peer transport address.

servicecreator.py: iterate connection blocks and create new direct connection servers for them.

uploadblocks.py: iterate a communicator's upload queue and upload the blocks to connected peers