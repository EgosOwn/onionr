"""Onionr - Private P2P Communication.

Lookup new peer transport addresses using the communicator
"""
from typing import TYPE_CHECKING
import logger
from onionrutils import stringvalidators
from communicator import peeraction, onlinepeers
from utils import gettransports
import onionrexceptions


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


def lookup_new_peer_transports_with_communicator(shared_state):
    logger.info('Looking up new addresses...')
    tryAmount = 1
    newPeers = []
    transports = gettransports.get()
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")

    for i in range(tryAmount):
        # Download new peer address list from random online peers
        if len(newPeers) > 10000:
            # Don't get new peers if we have too many queued up
            break
        try:
            peer = onlinepeers.pick_online_peer(kv)
            newAdders = peeraction.peer_action(shared_state, peer, action='pex')
        except onionrexceptions.OnlinePeerNeeded:
            continue
        try:
            newPeers = newAdders.split(',')
        except AttributeError:
            pass
    else:
        # Validate new peers are good format and not already in queue
        invalid = []
        for x in newPeers:
            x = x.strip()
            if not stringvalidators.validate_transport(x) \
                    or x in kv.get('newPeers') or x in transports:
                # avoid adding if its our address
                invalid.append(x)
        for x in invalid:
            try:
                newPeers.remove(x)
            except ValueError:
                pass
        kv.get('newPeers').extend(newPeers)