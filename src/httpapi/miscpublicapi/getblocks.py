"""Onionr - Private P2P Communication.

Public endpoints to get block data and lists
"""
from flask import Response, abort

import config
from onionrutils import bytesconverter, stringvalidators
from coredb import blockmetadb
from utils import reconstructhash
from onionrblocks import BlockList
from onionrblocks.onionrblockapi import Block
from .. import apiutils
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


def get_public_block_list(public_API, request):
    # Provide a list of our blocks, with a date offset
    date_adjust = request.args.get('date')
    type_filter = request.args.get('type')
    b_list = blockmetadb.get_block_list(date_rec=date_adjust)
    share_list = ''
    if config.get('general.hide_created_blocks', True):
        for b in public_API.hideBlocks:
            if b in b_list:
                # Don't share blocks we created if they haven't been *uploaded* yet, makes it harder to find who created a block
                b_list.remove(b)
    for b in b_list:
        if type_filter:
            if Block(b, decrypt=False).getType() != type_filter:
                continue
        share_list += '%s\n' % (reconstructhash.deconstruct_hash(b),)
    return Response(share_list)


def get_block_data(public_API, b_hash):
    """return block data by hash unless we are hiding it"""
    resp = ''
    b_hash = reconstructhash.reconstruct_hash(b_hash)
    if stringvalidators.validate_hash(b_hash):
        if not config.get('general.hide_created_blocks', True) \
                or b_hash not in public_API.hideBlocks:
            if b_hash in public_API._too_many.get(BlockList).get():
                block = apiutils.GetBlockData().get_block_data(
                    b_hash, raw=True, decrypt=False)
                try:
                    # Encode in case data is binary
                    block = block.encode('utf-8')
                except AttributeError:
                    # 404 if no block data
                    if not block:
                        abort(404)
                    if not len(block):
                        abort(404)
                resp = block
    if len(resp) == 0:
        abort(404)
        resp = ""
    # Has to be octet stream, otherwise binary data fails hash check
    return Response(resp, mimetype='application/octet-stream')
