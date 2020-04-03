"""Onionr - Private P2P Communication.

Test Onionr as it is running
"""
import sys
import sqlite3

import onionrstorage
import onionrexceptions
import onionrcrypto as crypto
import filepaths
from onionrblocks import storagecounter
from coredb import dbfiles
from onionrutils import blockmetadata, bytesconverter
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


def set_data(data, mimc_hash) -> str:
    """Set the data assciated with a hash."""
    storage_counter = storagecounter.StorageCounter()
    data = data
    dataSize = sys.getsizeof(data)
    nonce_hash = crypto.hashers.sha3_hash(
        bytesconverter.str_to_bytes(
            blockmetadata.fromdata.get_block_metadata_from_data(data)[2]))
    nonce_hash = bytesconverter.bytes_to_str(nonce_hash)

    if not type(data) is bytes:
        data = data.encode()

    mimc_hash = crypto.hashers.sha3_hash(data)

    if type(mimc_hash) is bytes:
        mimc_hash = mimc_hash.decode()
    try:
        onionrstorage.getData(mimc_hash)
    except onionrexceptions.NoDataAvailable:
        if storage_counter.add_bytes(dataSize) is not False:
            onionrstorage.store(data, blockHash=mimc_hash)
            conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
            c = conn.cursor()
            c.execute(
                "UPDATE hashes SET dataSaved=1 WHERE hash = ?;",
                (mimc_hash,))
            conn.commit()
            conn.close()
            with open(filepaths.data_nonce_file, 'a') as nonceFile:
                nonceFile.write(nonce_hash + '\n')
        else:
            raise onionrexceptions.DiskAllocationReached
    else:
        raise onionrexceptions.DataExists(
                "Data is already set for " + mimc_hash)

    return mimc_hash
