'''
    Onionr - Private P2P Communication

    Accept block uploads to the public API server
'''
from gevent import spawn
from gevent import threading

import sys
from flask import Response
from flask import abort

from onionrutils import localcommand
from onionrblocks import blockimporter
import onionrexceptions
import logger

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


def accept_upload(request):
    """Accept uploaded blocks to our public Onionr protocol API server"""
    resp = 'failure'
    data = request.get_data()
    b_hash = ''
    if sys.getsizeof(data) < 100000000:
        try:
            b_hash = blockimporter.import_block_from_data(data)
            if b_hash:
                spawn(
                    localcommand.local_command,
                    f'/daemon-event/upload_event',
                    post=True,
                    is_json=True,
                    postData={'block': b_hash}
                    ).get(timeout=10)
                resp = 'success'
            else:
                resp = 'failure'
                logger.warn(f'Error encountered importing uploaded block {b_hash}')
        except onionrexceptions.BlacklistedBlock:
            logger.debug('uploaded block is blacklisted')
            resp = 'failure'
        except onionrexceptions.InvalidProof:
            resp = 'proof'
        except onionrexceptions.DataExists:
            resp = 'exists'
    if resp == 'failure':
        abort(400)
    elif resp == 'proof':
        resp = Response(resp, 400)
        logger.warn(f'Error encountered importing uploaded block, invalid proof {b_hash}')
    else:
        resp = Response(resp)
    return resp
