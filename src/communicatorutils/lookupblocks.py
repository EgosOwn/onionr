'''
    Onionr - Private P2P Communication

    Lookup new blocks with the communicator using a random connected peer
'''
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import logger, onionrproofs
from onionrutils import stringvalidators, epoch
from communicator import peeraction, onlinepeers
from coredb import blockmetadb
from utils import reconstructhash
from onionrblocks import onionrblacklist
blacklist = onionrblacklist.OnionrBlackList()
def lookup_blocks_from_communicator(comm_inst):
    logger.info('Looking up new blocks')
    tryAmount = 2
    newBlocks = ''
    existingBlocks = blockmetadb.get_block_list() # List of existing saved blocks
    triedPeers = [] # list of peers we've tried this time around
    maxBacklog = 1560 # Max amount of *new* block hashes to have already in queue, to avoid memory exhaustion
    lastLookupTime = 0 # Last time we looked up a particular peer's list
    new_block_count = 0
    for i in range(tryAmount):
        listLookupCommand = 'getblocklist' # This is defined here to reset it each time
        if len(comm_inst.blockQueue) >= maxBacklog:
            break
        if not comm_inst.isOnline:
            break
        # check if disk allocation is used
        if comm_inst.storage_counter.is_full():
            logger.debug('Not looking up new blocks due to maximum amount of allowed disk space used')
            break
        peer = onlinepeers.pick_online_peer(comm_inst) # select random online peer
        # if we've already tried all the online peers this time around, stop
        if peer in triedPeers:
            if len(comm_inst.onlinePeers) == len(triedPeers):
                break
            else:
                continue
        triedPeers.append(peer)

        # Get the last time we looked up a peer's stamp to only fetch blocks since then.
        # Saved in memory only for privacy reasons
        try:
            lastLookupTime = comm_inst.dbTimestamps[peer]
        except KeyError:
            lastLookupTime = 0
        else:
            listLookupCommand += '?date=%s' % (lastLookupTime,)
        try:
            newBlocks = peeraction.peer_action(comm_inst, peer, listLookupCommand) # get list of new block hashes
        except Exception as error:
            logger.warn('Could not get new blocks from %s.' % peer, error = error)
            newBlocks = False
        else:
            comm_inst.dbTimestamps[peer] = epoch.get_rounded_epoch(roundS=60)
        if newBlocks != False:
            # if request was a success
            for i in newBlocks.split('\n'):
                if stringvalidators.validate_hash(i):
                    i = reconstructhash.reconstruct_hash(i)
                    # if newline seperated string is valid hash
                    if not i in existingBlocks:
                        # if block does not exist on disk and is not already in block queue
                        if i not in comm_inst.blockQueue:
                            if onionrproofs.hashMeetsDifficulty(i) and not blacklist.inBlacklist(i):
                                if len(comm_inst.blockQueue) <= 1000000:
                                    comm_inst.blockQueue[i] = [peer] # add blocks to download queue
                                    new_block_count += 1
                        else:
                            if peer not in comm_inst.blockQueue[i]:
                                if len(comm_inst.blockQueue[i]) < 10:
                                    comm_inst.blockQueue[i].append(peer)
    if new_block_count > 0:
        block_string = ""
        if new_block_count > 1:
            block_string = "s"
        logger.info('Discovered %s new block%s' % (new_block_count, block_string), terminal=True)
        comm_inst.download_blocks_timer.count = int(comm_inst.download_blocks_timer.frequency * 0.99)
    comm_inst.decrementThreadCount('lookup_blocks_from_communicator')
    return