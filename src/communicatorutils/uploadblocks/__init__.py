'''
    Onionr - Private P2P Communication

    Upload blocks in the upload queue to peers from the communicator
'''
from __future__ import annotations
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
from typing import Union, TYPE_CHECKING
import logger
from communicatorutils import proxypicker
import onionrexceptions
from onionrblocks import onionrblockapi as block
from onionrutils import localcommand, stringvalidators, basicrequests
from communicator import onlinepeers
import onionrcrypto
from . import sessionmanager

def upload_blocks_from_communicator(comm_inst: OnionrCommunicatorDaemon):
    """Accepts a communicator instance and uploads blocks from its upload queue"""
    """when inserting a block, we try to upload
     it to a few peers to add some deniability & increase functionality"""
    TIMER_NAME = "upload_blocks_from_communicator"

    session_manager: sessionmanager.BlockUploadSessionManager = comm_inst.shared_state.get(sessionmanager.BlockUploadSessionManager)
    triedPeers = []
    finishedUploads = []
    comm_inst.blocksToUpload = onionrcrypto.cryptoutils.random_shuffle(comm_inst.blocksToUpload)
    if len(comm_inst.blocksToUpload) != 0:
        for bl in comm_inst.blocksToUpload:
            if not stringvalidators.validate_hash(bl):
                logger.warn('Requested to upload invalid block', terminal=True)
                comm_inst.decrementThreadCount(TIMER_NAME)
                return
            session = session_manager.add_session(bl)
            for i in range(min(len(comm_inst.onlinePeers), 6)):
                peer = onlinepeers.pick_online_peer(comm_inst)
                try:
                    session.peer_exists[peer]
                    continue
                except KeyError:
                    pass
                try:
                    if session.peer_fails[peer] > 3: continue
                except KeyError:
                    pass
                if peer in triedPeers: continue
                triedPeers.append(peer)
                url = f'http://{peer}/upload'
                try:
                    data = block.Block(bl).getRaw()
                except onionrexceptions.NoDataAvailable:
                    finishedUploads.append(bl)
                    break
                proxyType = proxypicker.pick_proxy(peer)
                logger.info(f"Uploading block {bl[:8]} to {peer}", terminal=True)
                resp = basicrequests.do_post_request(url, data=data, proxyType=proxyType, content_type='application/octet-stream')
                if not resp == False:
                    if resp == 'success':
                        session.success()
                        session.peer_exists[peer] = True
                    elif resp == 'exists':
                        session.success()
                        session.peer_exists[peer] = True
                    else:
                        session.fail()
                        session.fail_peer(peer)
                        comm_inst.getPeerProfileInstance(peer).addScore(-5)
                        logger.warn(f'Failed to upload {bl[:8]}, reason: {resp[:15]}', terminal=True)
                else:
                    session.fail()
        session_manager.clean_session()
    for x in finishedUploads:
        try:
            comm_inst.blocksToUpload.remove(x)
        except ValueError:
            pass
    comm_inst.decrementThreadCount(TIMER_NAME)
