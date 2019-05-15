'''
    Onionr - P2P Microblogging Platform & Social network

    Download blocks using the communicator instance
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
import communicator, onionrexceptions
import logger, onionrpeers

def download_blocks_from_communicator(comm_inst):
    assert isinstance(comm_inst, communicator.OnionrCommunicatorDaemon)
    for blockHash in list(comm_inst.blockQueue):
        if len(comm_inst.onlinePeers) == 0:
            break
        triedQueuePeers = [] # List of peers we've tried for a block
        try:
            blockPeers = list(comm_inst.blockQueue[blockHash])
        except KeyError:
            blockPeers = []
        removeFromQueue = True
        if comm_inst.shutdown or not comm_inst.isOnline:
            # Exit loop if shutting down or offline
            break
        # Do not download blocks being downloaded or that are already saved (edge cases)
        if blockHash in comm_inst.currentDownloading:
            #logger.debug('Already downloading block %s...' % blockHash)
            continue
        if blockHash in comm_inst._core.getBlockList():
            #logger.debug('Block %s is already saved.' % (blockHash,))
            try:
                del comm_inst.blockQueue[blockHash]
            except KeyError:
                pass
            continue
        if comm_inst._core._blacklist.inBlacklist(blockHash):
            continue
        if comm_inst._core._utils.storageCounter.isFull():
            break
        comm_inst.currentDownloading.append(blockHash) # So we can avoid concurrent downloading in other threads of same block
        if len(blockPeers) == 0:
            peerUsed = comm_inst.pickOnlinePeer()
        else:
            blockPeers = comm_inst._core._crypto.randomShuffle(blockPeers)
            peerUsed = blockPeers.pop(0)

        if not comm_inst.shutdown and peerUsed.strip() != '':
            logger.info("Attempting to download %s from %s..." % (blockHash[:12], peerUsed))
        content = comm_inst.peerAction(peerUsed, 'getdata/' + blockHash) # block content from random peer (includes metadata)
        if content != False and len(content) > 0:
            try:
                content = content.encode()
            except AttributeError:
                pass

            realHash = comm_inst._core._crypto.sha3Hash(content)
            try:
                realHash = realHash.decode() # bytes on some versions for some reason
            except AttributeError:
                pass
            if realHash == blockHash:
                content = content.decode() # decode here because sha3Hash needs bytes above
                metas = comm_inst._core._utils.getBlockMetadataFromData(content) # returns tuple(metadata, meta), meta is also in metadata
                metadata = metas[0]
                if comm_inst._core._utils.validateMetadata(metadata, metas[2]): # check if metadata is valid, and verify nonce
                    if comm_inst._core._crypto.verifyPow(content): # check if POW is enough/correct
                        logger.info('Attempting to save block %s...' % blockHash[:12])
                        try:
                            comm_inst._core.setData(content)
                        except onionrexceptions.DiskAllocationReached:
                            logger.error('Reached disk allocation allowance, cannot save block %s.' % blockHash)
                            removeFromQueue = False
                        else:
                            comm_inst._core.addToBlockDB(blockHash, dataSaved=True)
                            comm_inst._core._utils.processBlockMetadata(blockHash) # caches block metadata values to block database
                    else:
                        logger.warn('POW failed for block %s.' % blockHash)
                else:
                    if comm_inst._core._blacklist.inBlacklist(realHash):
                        logger.warn('Block %s is blacklisted.' % (realHash,))
                    else:
                        logger.warn('Metadata for block %s is invalid.' % blockHash)
                        comm_inst._core._blacklist.addToDB(blockHash)
            else:
                # if block didn't meet expected hash
                tempHash = comm_inst._core._crypto.sha3Hash(content) # lazy hack, TODO use var
                try:
                    tempHash = tempHash.decode()
                except AttributeError:
                    pass
                # Punish peer for sharing invalid block (not always malicious, but is bad regardless)
                onionrpeers.PeerProfiles(peerUsed, comm_inst._core).addScore(-50)
                if tempHash != 'ed55e34cb828232d6c14da0479709bfa10a0923dca2b380496e6b2ed4f7a0253':
                    # Dumb hack for 404 response from peer. Don't log it if 404 since its likely not malicious or a critical error.
                    logger.warn('Block hash validation failed for ' + blockHash + ' got ' + tempHash)
                else:
                    removeFromQueue = False # Don't remove from queue if 404
            if removeFromQueue:
                try:
                    del comm_inst.blockQueue[blockHash] # remove from block queue both if success or false
                except KeyError:
                    pass
        comm_inst.currentDownloading.remove(blockHash)
    comm_inst.decrementThreadCount('getBlocks')