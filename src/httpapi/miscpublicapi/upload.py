"""Onionr - Private P2P Communication.

Accept block uploads to the public API server
"""
import sys

from gevent import spawn
from flask import Response
from flask import abort
from flask import g

from onionrutils import localcommand
from onionrblocks import blockimporter
import onionrexceptions
import logger
import config

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


def accept_upload(request):
    """Accept uploaded blocks to our public Onionr protocol API server"""
    resp = 'failure'
    data = request.get_data()
    data_size = sys.getsizeof(data)
    b_hash = None
    if data_size < 30:
        resp = 'size'
    elif data_size < 100000000:
        try:
            b_hash = blockimporter.import_block_from_data(data)
            if b_hash:
                # Upload mixing is where a node will hide and reupload a block
                # to act like it is also a creator
                # This adds deniability but is very slow
                if g.too_many.get_by_string(
                        "DeadSimpleKV").get('onlinePeers') and \
                        config.get('general.upload_mixing', False):
                    spawn(
                        localcommand.local_command,
                        '/daemon-event/upload_event',
                        post=True,
                        is_json=True,
                        post_data={'block': b_hash}
                        ).get(timeout=10)
                resp = 'success'
            else:
                resp = 'failure'
                logger.warn(
                    f'Error encountered importing uploaded block {b_hash}')
        except onionrexceptions.BlacklistedBlock:
            logger.debug('uploaded block is blacklisted')
            resp = 'failure'
        except onionrexceptions.InvalidProof:
            resp = 'proof'
        except onionrexceptions.DataExists:
            resp = 'exists'
        except onionrexceptions.PlaintextNotSupported:
            logger.debug(f"attempted plaintext upload to us: {b_hash}")
            resp = 'failure'
        except onionrexceptions.InvalidMetadata:
            logger.debug(
                f'uploaded block {b_hash} has invalid metadata')
            resp = 'failure'
    if resp == 'failure':
        abort(400)
    elif resp == 'size':
        resp = Response(resp, 400)
        logger.warn(
            f'Error importing uploaded block, invalid size {b_hash}')
    elif resp == 'proof':
        resp = Response(resp, 400)
        if b_hash:
            logger.warn(
                f'Error importing uploaded block, invalid proof {b_hash}')
        else:
            logger.warn(
                'Error importing uploaded block, invalid proof')
    else:
        resp = Response(resp)
    return resp
