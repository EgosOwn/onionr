"""
Onionr - Private P2P Communication.

Determine if our node is able to use Tor based
on the status of a communicator instance
and the result of pinging onion http servers
"""
import logger
from utils import netutils
from onionrutils import localcommand, epoch
from . import restarttor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def net_check(shared_state):
    """Check if we are connected to the internet.

    or not when we can't connect to any peers
    """
    # for detecting if we have received incoming connections recently
    rec = False
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    proxy_port = shared_state.get_by_string("NetController").socksPort

    if len(kv.get('onlinePeers')) == 0:
        try:
            if (epoch.get_epoch() - int(localcommand.local_command
                                        ('/lastconnect'))) <= 60:
                kv.put('isOnline', True)
                rec = True
        except ValueError:
            pass
        if not rec and not netutils.check_network(torPort=proxy_port):
            if not kv.get('shutdown'):
                if not shared_state.get_by_string(
                    "OnionrCommunicatorDaemon").config.get(
                        'general.offline_mode', False):
                    logger.warn('Network check failed, are you connected to ' +
                                'the Internet, and is Tor working? ' +
                                'This is usually temporary, but bugs and censorship can cause this to persist, in which case you should report it to beardog [at] mailbox.org',  # noqa
                                terminal=True)
                    restarttor.restart(shared_state)
                    kv.put('offlinePeers', [])
            kv.put('isOnline', False)
        else:
            kv.put('isOnline', True)
