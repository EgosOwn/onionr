'''
    Onionr - Private P2P Communication

    Creates an onionr direct connection service by scanning all connection blocks
'''
'''
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
'''
import communicator, onionrblockapi
from onionrutils import stringvalidators

def service_creator(daemon):
    assert isinstance(daemon, communicator.OnionrCommunicatorDaemon)
    core = daemon._core
    utils = core._utils
    
    # Find socket connection blocks
    # TODO cache blocks and only look at recently received ones
    con_blocks = core.getBlocksByType('con')
    for b in con_blocks:
        if not b in daemon.active_services:
            bl = onionrblockapi.Block(b, core=core, decrypt=True)
            bs = utils.bytesToStr(bl.bcontent) + '.onion'
            if utils.validatePubKey(bl.signer) and stringvalidators.validate_transport(bs):
                signer = utils.bytesToStr(bl.signer)
                daemon.active_services.append(b)
                daemon.active_services.append(signer)
                daemon.services.create_server(signer, bs)
    
    daemon.decrementThreadCount('service_creator')