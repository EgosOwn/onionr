import sqlite3
def get_expired_blocks(core_inst):
    '''Returns a list of expired blocks'''
    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()
    date = int(core_inst._utils.getEpoch())

    execute = 'SELECT hash FROM hashes WHERE expire <= %s ORDER BY dateReceived;' % (date,)

    rows = list()
    for row in c.execute(execute):
        for i in row:
            rows.append(i)
    conn.close()
    return rows