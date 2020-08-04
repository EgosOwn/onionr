from typing import TYPE_CHECKING

from onionrthreads import add_onionr_thread
from communicator.onlinepeers import get_online_peers

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
    from toomanyobjs import TooMany



def spawn_client_threads(shared_state: 'TooMany'):
    kv: 'DeadSimpleKV' = shared_state.get_by_string('DeadSimpleKV')
    add_onionr_thread(get_online_peers, (shared_state,), 3, 1)
