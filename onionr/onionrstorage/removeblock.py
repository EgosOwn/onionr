import sys, sqlite3
import onionrexceptions, onionrstorage
from onionrutils import stringvalidators
def remove_block(core_inst, block):
    '''
        remove a block from this node (does not automatically blacklist)

        **You may want blacklist.addToDB(blockHash)
    '''

    if stringvalidators.validate_hash(block):
        conn = sqlite3.connect(core_inst.blockDB, timeout=30)
        c = conn.cursor()
        t = (block,)
        c.execute('Delete from hashes where hash=?;', t)
        conn.commit()
        conn.close()
        dataSize = sys.getsizeof(onionrstorage.getData(core_inst, block))
        core_inst.storage_counter.removeBytes(dataSize)
    else:
        raise onionrexceptions.InvalidHexHash