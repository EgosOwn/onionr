import sqlite3
import logger
def list_peers(core_inst, randomOrder=True, getPow=False, trust=0):
    '''
        Return a list of public keys (misleading function name)

        randomOrder determines if the list should be in a random order
        trust sets the minimum trust to list
    '''
    conn = sqlite3.connect(core_inst.peerDB, timeout=30)
    c = conn.cursor()

    payload = ''

    if trust not in (0, 1, 2):
        logger.error('Tried to select invalid trust.')
        return

    if randomOrder:
        payload = 'SELECT * FROM peers WHERE trust >= ? ORDER BY RANDOM();'
    else:
        payload = 'SELECT * FROM peers WHERE trust >= ?;'

    peerList = []

    for i in c.execute(payload, (trust,)):
        try:
            if len(i[0]) != 0:
                if getPow:
                    peerList.append(i[0] + '-' + i[1])
                else:
                    peerList.append(i[0])
        except TypeError:
            pass

    conn.close()

    return peerList

def list_adders(core_inst, randomOrder=True, i2p=True, recent=0):
    '''
        Return a list of transport addresses
    '''
    conn = sqlite3.connect(core_inst.addressDB, timeout=30)
    c = conn.cursor()
    if randomOrder:
        addresses = c.execute('SELECT * FROM adders ORDER BY RANDOM();')
    else:
        addresses = c.execute('SELECT * FROM adders;')
    addressList = []
    for i in addresses:
        if len(i[0].strip()) == 0:
            continue
        addressList.append(i[0])
    conn.close()
    testList = list(addressList) # create new list to iterate
    for address in testList:
        try:
            if recent > 0 and (core_inst._utils.getEpoch() - core_inst.getAddressInfo(address, 'lastConnect')) > recent:
                raise TypeError # If there is no last-connected date or it was too long ago, don't add peer to list if recent is not 0
        except TypeError:
            addressList.remove(address)
    return addressList