'''
    Onionr - Private P2P Communication

    Upload blocks in the upload queue to peers from the communicator
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
import logger
from communicatorutils import proxypicker
import onionrblockapi as block
from onionrutils import localcommand, stringvalidators, basicrequests

def upload_blocks_from_communicator(comm_inst):
    # when inserting a block, we try to upload it to a few peers to add some deniability
    triedPeers = []
    finishedUploads = []
    core = comm_inst._core
    comm_inst.blocksToUpload = core._crypto.randomShuffle(comm_inst.blocksToUpload)
    if len(comm_inst.blocksToUpload) != 0:
        for bl in comm_inst.blocksToUpload:
            if not stringvalidators.validate_hash(bl):
                logger.warn('Requested to upload invalid block')
                comm_inst.decrementThreadCount('uploadBlock')
                return
            for i in range(min(len(comm_inst.onlinePeers), 6)):
                peer = comm_inst.pickOnlinePeer()
                if peer in triedPeers:
                    continue
                triedPeers.append(peer)
                url = 'http://' + peer + '/upload'
                data = {'block': block.Block(bl).getRaw()}
                proxyType = proxypicker.pick_proxy(peer)
                logger.info("Uploading block to " + peer)
                if not basicrequests.do_post_request(core, url, data=data, proxyType=proxyType) == False:
                    localcommand.local_command(core, 'waitforshare/' + bl, post=True)
                    finishedUploads.append(bl)
    for x in finishedUploads:
        try:
            comm_inst.blocksToUpload.remove(x)
        except ValueError:
            pass
    comm_inst.decrementThreadCount('uploadBlock')