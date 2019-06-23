import sqlite3
import onionrevents as events
from onionrutils import stringvalidators

def remove_address(core_inst, address):
    '''
        Remove an address from the address database
    '''

    if stringvalidators.validate_transport(address):
        conn = sqlite3.connect(core_inst.addressDB, timeout=30)
        c = conn.cursor()
        t = (address,)
        c.execute('Delete from adders where address=?;', t)
        conn.commit()
        conn.close()

        events.event('address_remove', data = {'address': address}, onionr = core_inst.onionrInst)
        return True
    else:
        return False