import sys, sqlite3
import onionrexceptions, onionrstorage
from onionrutils import stringvalidators
from coredb import dbfiles
from onionrblocks import storagecounter
def remove_block(block):
    '''
        remove a block from this node (does not automatically blacklist)

        **You may want blacklist.addToDB(blockHash)
    '''

    if stringvalidators.validate_hash(block):
        conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
        c = conn.cursor()
        t = (block,)
        c.execute('Delete from hashes where hash=?;', t)
        conn.commit()
        conn.close()
        dataSize = sys.getsizeof(onionrstorage.getData(block))
        storagecounter.StorageCounter().remove_bytes(dataSize)
    else:
        raise onionrexceptions.InvalidHexHash