import sys, sqlite3
import onionrstorage, onionrexceptions, onionrcrypto as crypto
import filepaths, storagecounter
from coredb import dbfiles
from onionrutils import blockmetadata, bytesconverter
def set_data(data)->str:
    '''
        Set the data assciated with a hash
    '''
    storage_counter = storagecounter.StorageCounter()
    data = data
    dataSize = sys.getsizeof(data)
    nonce_hash = crypto.hashers.sha3_hash(bytesconverter.str_to_bytes(blockmetadata.fromdata.get_block_metadata_from_data(data)[2]))
    nonce_hash = bytesconverter.bytes_to_str(nonce_hash)

    if not type(data) is bytes:
        data = data.encode()

    dataHash = crypto.hashers.sha3_hash(data)

    if type(dataHash) is bytes:
        dataHash = dataHash.decode()
    blockFileName = filepaths.block_data_location + dataHash + '.dat'
    try:
        onionrstorage.getData(dataHash)
    except onionrexceptions.NoDataAvailable:
        if storage_counter.add_bytes(dataSize) != False:
            onionrstorage.store(data, blockHash=dataHash)
            conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
            c = conn.cursor()
            c.execute("UPDATE hashes SET dataSaved=1 WHERE hash = ?;", (dataHash,))
            conn.commit()
            conn.close()
            with open(filepaths.data_nonce_file, 'a') as nonceFile:
                nonceFile.write(nonce_hash + '\n')
        else:
            raise onionrexceptions.DiskAllocationReached
    else:
        raise onionrexceptions.DataExists("Data is already set for " + dataHash)

    return dataHash