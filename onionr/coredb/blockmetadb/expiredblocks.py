import sqlite3
from onionrutils import epoch
def get_expired_blocks(core_inst):
    '''Returns a list of expired blocks'''
    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()
    date = int(epoch.get_epoch())

    execute = 'SELECT hash FROM hashes WHERE expire <= %s ORDER BY dateReceived;' % (date,)

    rows = list()
    for row in c.execute(execute):
        for i in row:
            rows.append(i)
    conn.close()
    return rows