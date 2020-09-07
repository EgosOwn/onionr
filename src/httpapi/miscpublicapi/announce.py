"""Onionr - Private P2P Communication.

Handle announcements to the public API server
"""
from flask import Response, g
import deadsimplekv

import logger
from etc import onionrvalues
from onionrutils import stringvalidators, bytesconverter
import filepaths
"""
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
"""


def handle_announce(request):
    """accept announcement posts, validating POW
    clientAPI should be an instance of the clientAPI server running,
    request is a instance of a flask request
    """
    resp = 'failure'
    newNode = ''

    try:
        newNode = request.form['node'].encode()
    except KeyError:
        logger.warn('No node specified for upload')
    else:
        newNode = bytesconverter.bytes_to_str(newNode)
        announce_queue = deadsimplekv.DeadSimpleKV(filepaths.announce_cache)
        announce_queue_list = announce_queue.get('new_peers')
        if announce_queue_list is None:
            announce_queue_list = []
        else:
            if len(announce_queue_list) >= onionrvalues.MAX_NEW_PEER_QUEUE:
                newNode = ''

        if stringvalidators.validate_transport(newNode) and \
                newNode not in announce_queue_list:
            g.shared_state.get(
                deadsimplekv.DeadSimpleKV).get('newPeers').append(newNode)
            announce_queue.put('new_peers',
                               announce_queue_list.append(newNode))
            announce_queue.flush()
            resp = 'Success'

    resp = Response(resp)
    if resp == 'failure':
        return resp, 406
    return resp