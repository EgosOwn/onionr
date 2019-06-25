import sqlite3
import onionrevents as events
from onionrutils import stringvalidators

def add_peer(core_inst, peerID, name=''):
    '''
        Adds a public key to the key database (misleading function name)
    '''
    if peerID in core_inst.listPeers() or peerID == core_inst._crypto.pubKey:
        raise ValueError("specified id is already known")

    # This function simply adds a peer to the DB
    if not stringvalidators.validate_pub_key(peerID):
        return False

    events.event('pubkey_add', data = {'key': peerID}, onionr = core_inst.onionrInst)

    conn = sqlite3.connect(core_inst.peerDB, timeout=30)
    hashID = core_inst._crypto.pubKeyHashID(peerID)
    c = conn.cursor()
    t = (peerID, name, 'unknown', hashID, 0)

    for i in c.execute("SELECT * FROM peers WHERE id = ?;", (peerID,)):
        try:
            if i[0] == peerID:
                conn.close()
                return False
        except ValueError:
            pass
        except IndexError:
            pass
    c.execute('INSERT INTO peers (id, name, dateSeen, hashID, trust) VALUES(?, ?, ?, ?, ?);', t)
    conn.commit()
    conn.close()

    return True

def add_address(core_inst, address):
    '''
        Add an address to the address database (only tor currently)
    '''

    if type(address) is None or len(address) == 0:
        return False
    if stringvalidators.validate_transport(address):
        if address == core_inst.config.get('i2p.ownAddr', None) or address == core_inst.hsAddress:
            return False
        conn = sqlite3.connect(core_inst.addressDB, timeout=30)
        c = conn.cursor()
        # check if address is in database
        # this is safe to do because the address is validated above, but we strip some chars here too just in case
        address = address.replace('\'', '').replace(';', '').replace('"', '').replace('\\', '')
        for i in c.execute("SELECT * FROM adders WHERE address = ?;", (address,)):
            try:
                if i[0] == address:
                    conn.close()
                    return False
            except ValueError:
                pass
            except IndexError:
                pass

        t = (address, 1)
        c.execute('INSERT INTO adders (address, type) VALUES(?, ?);', t)
        conn.commit()
        conn.close()

        events.event('address_add', data = {'address': address}, onionr = core_inst.onionrInst)

        return True
    else:
        return False
