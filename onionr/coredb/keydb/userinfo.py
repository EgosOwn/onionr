import sqlite3
def get_user_info(core_inst, peer, info):
    '''
        Get info about a peer from their database entry

        id text             0
        name text,          1
        adders text,        2
        dateSeen not null,  3
        trust int           4
        hashID text         5
    '''
    conn = sqlite3.connect(core_inst.peerDB, timeout=30)
    c = conn.cursor()

    command = (peer,)
    infoNumbers = {'id': 0, 'name': 1, 'adders': 2, 'dateSeen': 3, 'trust': 4, 'hashID': 5}
    info = infoNumbers[info]
    iterCount = 0
    retVal = ''

    for row in c.execute('SELECT * FROM peers WHERE id=?;', command):
        for i in row:
            if iterCount == info:
                retVal = i
                break
            else:
                iterCount += 1

    conn.close()

    return retVal

def set_peer_info(core_inst, peer, key, data):
    '''
        Update a peer for a key
    '''

    conn = sqlite3.connect(core_inst.peerDB, timeout=30)
    c = conn.cursor()

    command = (data, peer)

    # TODO: validate key on whitelist
    if key not in ('id', 'name', 'pubkey', 'forwardKey', 'dateSeen', 'trust'):
        raise Exception("Got invalid database key when setting peer info")

    c.execute('UPDATE peers SET ' + key + ' = ? WHERE id=?', command)
    conn.commit()
    conn.close()