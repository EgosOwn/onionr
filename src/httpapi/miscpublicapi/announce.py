'''
    Onionr - Private P2P Communication

    Handle announcements to the public API server
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
import base64
from flask import Response, g
import deadsimplekv
import logger
from etc import onionrvalues
from onionrutils import stringvalidators, bytesconverter
from utils import gettransports
import onionrcrypto as crypto, filepaths
from communicator import OnionrCommunicatorDaemon
def handle_announce(request):
    '''
    accept announcement posts, validating POW
    clientAPI should be an instance of the clientAPI server running, request is a instance of a flask request
    '''
    resp = 'failure'
    powHash = ''
    randomData = ''
    newNode = ''

    try:
        newNode = request.form['node'].encode()
    except KeyError:
        logger.warn('No node specified for upload')
        pass
    else:
        try:
            randomData = request.form['random']
            randomData = base64.b64decode(randomData)
        except KeyError:
            logger.warn('No random data specified for upload')
        else:
            nodes = newNode + bytesconverter.str_to_bytes(gettransports.get()[0])
            nodes = crypto.hashers.blake2b_hash(nodes)
            powHash = crypto.hashers.blake2b_hash(randomData + nodes)
            try:
                powHash = powHash.decode()
            except AttributeError:
                pass
            if powHash.startswith('0' * onionrvalues.ANNOUNCE_POW):
                newNode = bytesconverter.bytes_to_str(newNode)
                announce_queue = deadsimplekv.DeadSimpleKV(filepaths.announce_cache)
                announce_queue_list = announce_queue.get('new_peers')
                if announce_queue_list is None:
                    announce_queue_list = []

                if stringvalidators.validate_transport(newNode) and not newNode in announce_queue_list:
                    #clientAPI.onionrInst.communicatorInst.newPeers.append(newNode)
                    g.shared_state.get(OnionrCommunicatorDaemon).newPeers.append(newNode)
                    announce_queue.put('new_peers', announce_queue_list.append(newNode))
                    announce_queue.flush()
                    resp = 'Success'
            else:
                logger.warn(newNode.decode() + ' failed to meet POW: ' + powHash)
    resp = Response(resp)
    if resp == 'failure':
        return resp, 406
    return resp