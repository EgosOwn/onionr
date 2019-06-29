import sys, sqlite3
import onionrstorage, onionrexceptions
def set_data(core_inst, data):
    '''
        Set the data assciated with a hash
    '''

    data = data
    dataSize = sys.getsizeof(data)

    if not type(data) is bytes:
        data = data.encode()

    dataHash = core_inst._crypto.sha3Hash(data)

    if type(dataHash) is bytes:
        dataHash = dataHash.decode()
    blockFileName = core_inst.blockDataLocation + dataHash + '.dat'
    try:
        onionrstorage.getData(core_inst, dataHash)
    except onionrexceptions.NoDataAvailable:
        if core_inst.storage_counter.addBytes(dataSize) != False:
            onionrstorage.store(core_inst, data, blockHash=dataHash)
            conn = sqlite3.connect(core_inst.blockDB, timeout=30)
            c = conn.cursor()
            c.execute("UPDATE hashes SET dataSaved=1 WHERE hash = ?;", (dataHash,))
            conn.commit()
            conn.close()
            with open(core_inst.dataNonceFile, 'a') as nonceFile:
                nonceFile.write(dataHash + '\n')
        else:
            raise onionrexceptions.DiskAllocationReached
    else:
        raise onionrexceptions.DataExists("Data is already set for " + dataHash)

    return dataHash