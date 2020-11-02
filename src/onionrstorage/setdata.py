"""Onionr - Private P2P Communication.

Test Onionr as it is running
"""
import sys
import sqlite3

import onionrstorage
import onionrexceptions
import onionrcrypto as crypto
import filepaths
from onionrblocks import storagecounter, blockmetadata
from coredb import dbfiles
from onionrutils import bytesconverter
from etc.onionrvalues import DATABASE_LOCK_TIMEOUT
from onionrtypes import BlockHash
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
storage_counter = storagecounter.StorageCounter()


def set_data(data) -> BlockHash:
    """Set the data assciated with a hash."""
    data = data
    dataSize = sys.getsizeof(data)
    nonce_hash = crypto.hashers.sha3_hash(
        bytesconverter.str_to_bytes(
            blockmetadata.fromdata.get_block_metadata_from_data(data)[2]))
    nonce_hash = bytesconverter.bytes_to_str(nonce_hash)

    if not type(data) is bytes:
        data = data.encode()

    dataHash = crypto.hashers.sha3_hash(data)

    if type(dataHash) is bytes:
        dataHash = dataHash.decode()
    try:
        onionrstorage.getData(dataHash)
    except onionrexceptions.NoDataAvailable:
        if storage_counter.add_bytes(dataSize) is not False:
            onionrstorage.store(data, block_hash=dataHash)
            conn = sqlite3.connect(
                dbfiles.block_meta_db, timeout=DATABASE_LOCK_TIMEOUT)
            c = conn.cursor()
            c.execute(
                "UPDATE hashes SET dataSaved=1 WHERE hash = ?;",
                (dataHash,))
            conn.commit()
            conn.close()
            with open(filepaths.data_nonce_file, 'a') as nonceFile:
                nonceFile.write(nonce_hash + '\n')
        else:
            raise onionrexceptions.DiskAllocationReached
    else:
        raise onionrexceptions.DataExists(
                "Data is already set for " + dataHash)

    return dataHash
