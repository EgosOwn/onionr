'''
    Onionr - Private P2P Communication

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
from onionrutils import blockmetadata, stringvalidators, validatemetadata
from coredb import blockmetadb
from . import shoulddownload
from communicator import peeraction, onlinepeers
import onionrcrypto, onionrstorage, onionrblacklist, storagecounter
def download_blocks_from_communicator(comm_inst):
    '''Use Onionr communicator instance to download blocks in the communicator's queue'''
    assert isinstance(comm_inst, communicator.OnionrCommunicatorDaemon)
    blacklist = onionrblacklist.OnionrBlackList()
    storage_counter = storagecounter.StorageCounter()
    LOG_SKIP_COUNT = 50 # for how many iterations we skip logging the counter
    count = 0
    # Iterate the block queue in the communicator
    for blockHash in list(comm_inst.blockQueue):
        count += 1
        if len(comm_inst.onlinePeers) == 0:
            break
        triedQueuePeers = [] # List of peers we've tried for a block
        try:
            blockPeers = list(comm_inst.blockQueue[blockHash])
        except KeyError:
            blockPeers = []
        removeFromQueue = True

        if not shoulddownload.should_download(comm_inst, blockHash):
            continue

        if comm_inst.shutdown or not comm_inst.isOnline or storage_counter.is_full():
            # Exit loop if shutting down or offline, or disk allocation reached
            break
        # Do not download blocks being downloaded
        if blockHash in comm_inst.currentDownloading:
            #logger.debug('Already downloading block %s...' % blockHash)
            continue

        comm_inst.currentDownloading.append(blockHash) # So we can avoid concurrent downloading in other threads of same block
        if len(blockPeers) == 0:
            peerUsed = onlinepeers.pick_online_peer(comm_inst)
        else:
            blockPeers = onionrcrypto.cryptoutils.random_shuffle(blockPeers)
            peerUsed = blockPeers.pop(0)

        if not comm_inst.shutdown and peerUsed.strip() != '':
            logger.info("Attempting to download %s from %s..." % (blockHash[:12], peerUsed))
        content = peeraction.peer_action(comm_inst, peerUsed, 'getdata/' + blockHash, max_resp_size=3000000) # block content from random peer (includes metadata)

        if content != False and len(content) > 0:
            try:
                content = content.encode()
            except AttributeError:
                pass

            realHash = onionrcrypto.hashers.sha3_hash(content)
            try:
                realHash = realHash.decode() # bytes on some versions for some reason
            except AttributeError:
                pass
            if realHash == blockHash:
                content = content.decode() # decode here because sha3Hash needs bytes above
                metas = blockmetadata.get_block_metadata_from_data(content) # returns tuple(metadata, meta), meta is also in metadata
                metadata = metas[0]
                if validatemetadata.validate_metadata(metadata, metas[2]): # check if metadata is valid, and verify nonce
                    if onionrcrypto.cryptoutils.verify_POW(content): # check if POW is enough/correct
                        logger.info('Attempting to save block %s...' % blockHash[:12])
                        try:
                            onionrstorage.set_data(content)
                        except onionrexceptions.DataExists:
                            logger.warn('Data is already set for %s ' % (blockHash,))
                        except onionrexceptions.DiskAllocationReached:
                            logger.error('Reached disk allocation allowance, cannot save block %s.' % (blockHash,))
                            removeFromQueue = False
                        else:
                            blockmetadb.add_to_block_DB(blockHash, dataSaved=True) # add block to meta db
                            blockmetadata.process_block_metadata(blockHash) # caches block metadata values to block database
                    else:
                        logger.warn('POW failed for block %s.' % (blockHash,))
                else:
                    if blacklist.inBlacklist(realHash):
                        logger.warn('Block %s is blacklisted.' % (realHash,))
                    else:
                        logger.warn('Metadata for block %s is invalid.' % (blockHash,))
                        blacklist.addToDB(blockHash)
            else:
                # if block didn't meet expected hash
                tempHash = onionrcrypto.hashers.sha3_hash(content) # lazy hack, TODO use var
                try:
                    tempHash = tempHash.decode()
                except AttributeError:
                    pass
                # Punish peer for sharing invalid block (not always malicious, but is bad regardless)
                onionrpeers.PeerProfiles(peerUsed).addScore(-50)
                if tempHash != 'ed55e34cb828232d6c14da0479709bfa10a0923dca2b380496e6b2ed4f7a0253':
                    # Dumb hack for 404 response from peer. Don't log it if 404 since its likely not malicious or a critical error.
                    logger.warn('Block hash validation failed for ' + blockHash + ' got ' + tempHash)
                else:
                    removeFromQueue = False # Don't remove from queue if 404
            if removeFromQueue:
                try:
                    del comm_inst.blockQueue[blockHash] # remove from block queue both if success or false
                    if count == LOG_SKIP_COUNT:
                        logger.info('%s blocks remaining in queue' % [len(comm_inst.blockQueue)], terminal=True)
                        count = 0
                except KeyError:
                    pass
        comm_inst.currentDownloading.remove(blockHash)
    comm_inst.decrementThreadCount('getBlocks')