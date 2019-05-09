'''
    Onionr - P2P Microblogging Platform & Social network

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
def lookup_blocks_from_communicator(comm_inst):
        logger.info('Looking up new blocks...')
        tryAmount = 2
        newBlocks = ''
        existingBlocks = comm_inst._core.getBlockList()
        triedPeers = [] # list of peers we've tried this time around
        maxBacklog = 1560 # Max amount of *new* block hashes to have already in queue, to avoid memory exhaustion
        lastLookupTime = 0 # Last time we looked up a particular peer's list
        for i in range(tryAmount):
            listLookupCommand = 'getblocklist' # This is defined here to reset it each time
            if len(comm_inst.blockQueue) >= maxBacklog:
                break
            if not comm_inst.isOnline:
                break
            # check if disk allocation is used
            if comm_inst._core._utils.storageCounter.isFull():
                logger.debug('Not looking up new blocks due to maximum amount of allowed disk space used')
                break
            peer = comm_inst.pickOnlinePeer() # select random online peer
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
                newBlocks = comm_inst.peerAction(peer, listLookupCommand) # get list of new block hashes
            except Exception as error:
                logger.warn('Could not get new blocks from %s.' % peer, error = error)
                newBlocks = False
            else:
                comm_inst.dbTimestamps[peer] = comm_inst._core._utils.getRoundedEpoch(roundS=60)
            if newBlocks != False:
                # if request was a success
                for i in newBlocks.split('\n'):
                    if comm_inst._core._utils.validateHash(i):
                        # if newline seperated string is valid hash
                        if not i in existingBlocks:
                            # if block does not exist on disk and is not already in block queue
                            if i not in comm_inst.blockQueue:
                                if onionrproofs.hashMeetsDifficulty(i) and not comm_inst._core._blacklist.inBlacklist(i):
                                    if len(comm_inst.blockQueue) <= 1000000:
                                        comm_inst.blockQueue[i] = [peer] # add blocks to download queue
                            else:
                                if peer not in comm_inst.blockQueue[i]:
                                    if len(comm_inst.blockQueue[i]) < 10:
                                        comm_inst.blockQueue[i].append(peer)
        comm_inst.decrementThreadCount('lookupBlocks')
        return