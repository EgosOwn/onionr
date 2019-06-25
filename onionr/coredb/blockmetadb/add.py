import os, sqlite3
from onionrutils import epoch, blockmetadata
def add_to_block_DB(core_inst, newHash, selfInsert=False, dataSaved=False):
    '''
        Add a hash value to the block db

        Should be in hex format!
    '''

    if not os.path.exists(core_inst.blockDB):
        raise Exception('Block db does not exist')
    if blockmetadata.has_block(core_inst, newHash):
        return
    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()
    currentTime = epoch.get_epoch() + core_inst._crypto.secrets.randbelow(301)
    if selfInsert or dataSaved:
        selfInsert = 1
    else:
        selfInsert = 0
    data = (newHash, currentTime, '', selfInsert)
    c.execute('INSERT INTO hashes (hash, dateReceived, dataType, dataSaved) VALUES(?, ?, ?, ?);', data)
    conn.commit()
    conn.close()