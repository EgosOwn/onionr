import sqlite3
from . import expiredblocks, updateblockinfo
def get_block_list(core_inst, dateRec = None, unsaved = False):
    '''
        Get list of our blocks
    '''
    if dateRec == None:
        dateRec = 0

    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()

    execute = 'SELECT hash FROM hashes WHERE dateReceived >= ? ORDER BY dateReceived ASC;'
    args = (dateRec,)
    rows = list()
    for row in c.execute(execute, args):
        for i in row:
            rows.append(i)
    conn.close()
    return rows

def get_block_date(core_inst, blockHash):
    '''
        Returns the date a block was received
    '''

    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()

    execute = 'SELECT dateReceived FROM hashes WHERE hash=?;'
    args = (blockHash,)
    for row in c.execute(execute, args):
        for i in row:
            return int(i)
    conn.close()
    return None

def get_blocks_by_type(core_inst, blockType, orderDate=True):
    '''
        Returns a list of blocks by the type
    '''

    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()

    if orderDate:
        execute = 'SELECT hash FROM hashes WHERE dataType=? ORDER BY dateReceived;'
    else:
        execute = 'SELECT hash FROM hashes WHERE dataType=?;'

    args = (blockType,)
    rows = list()

    for row in c.execute(execute, args):
        for i in row:
            rows.append(i)
    conn.close()
    return rows