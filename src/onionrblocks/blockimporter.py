"""Onionr - Private P2P Communication.

Import block data and save it
"""
from onionrexceptions import BlacklistedBlock
from onionrexceptions import DiskAllocationReached
from onionrexceptions import InvalidProof
from onionrexceptions import InvalidMetadata
import logger
from onionrutils import validatemetadata
from onionrutils import bytesconverter
from coredb import blockmetadb
from onionrblocks import blockmetadata
import onionrstorage
import onionrcrypto as crypto
from . import onionrblacklist

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


def import_block_from_data(content):
    blacklist = onionrblacklist.OnionrBlackList()
    ret_data = False

    content = bytesconverter.str_to_bytes(content)

    data_hash = crypto.hashers.sha3_hash(content)

    if blacklist.inBlacklist(data_hash):
        raise BlacklistedBlock(f'%s is a blacklisted block {data_hash}')

    # returns tuple(metadata, meta), meta is also in metadata
    metas = blockmetadata.get_block_metadata_from_data(content)
    metadata = metas[0]

    # check if metadata is valid
    if validatemetadata.validate_metadata(metadata, metas[2]):
        # check if POW is enough/correct
        if crypto.cryptoutils.verify_POW(content):
            logger.info(f'Imported block passed proof, saving: {data_hash}.',
                        terminal=True)
            try:
                block_hash = onionrstorage.set_data(content)
            except DiskAllocationReached:
                logger.warn('Failed to save block due to full disk allocation')
                raise
            else:
                blockmetadb.add_to_block_DB(block_hash, dataSaved=True)
                # caches block metadata values to block database
                blockmetadata.process_block_metadata(block_hash)
                ret_data = block_hash
        else:
            raise InvalidProof
    else:
        raise InvalidMetadata
    return ret_data
