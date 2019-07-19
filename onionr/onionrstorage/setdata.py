import sys, sqlite3
import onionrstorage, onionrexceptions, onionrcrypto
import filepaths, storagecounter
from coredb import dbfiles
def set_data(data):
    '''
        Set the data assciated with a hash
    '''
    crypto = onionrcrypto.OnionrCrypto()
    storage_counter = storagecounter.StorageCounter()
    data = data
    dataSize = sys.getsizeof(data)

    if not type(data) is bytes:
        data = data.encode()

    dataHash = crypto.sha3Hash(data)

    if type(dataHash) is bytes:
        dataHash = dataHash.decode()
    blockFileName = filepaths.block_data_location + dataHash + '.dat'
    try:
        onionrstorage.getData(dataHash)
    except onionrexceptions.NoDataAvailable:
        if storage_counter.addBytes(dataSize) != False:
            onionrstorage.store(data, blockHash=dataHash)
            conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
            c = conn.cursor()
            c.execute("UPDATE hashes SET dataSaved=1 WHERE hash = ?;", (dataHash,))
            conn.commit()
            conn.close()
            with open(filepaths.data_nonce_file, 'a') as nonceFile:
                nonceFile.write(dataHash + '\n')
        else:
            raise onionrexceptions.DiskAllocationReached
    else:
        raise onionrexceptions.DataExists("Data is already set for " + dataHash)

    return dataHash