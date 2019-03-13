'''
    Onionr - P2P Anonymous Storage Network

    add keys (transport and pubkey)
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
import sys
import logger
def add_peer(o_inst):
    try:
        newPeer = sys.argv[2]
    except IndexError:
        pass
    else:
        if o_inst.onionrUtils.hasKey(newPeer):
            logger.info('We already have that key')
            return
        logger.info("Adding peer: " + logger.colors.underline + newPeer)
        try:
            if o_inst.onionrCore.addPeer(newPeer):
                logger.info('Successfully added key')
        except AssertionError:
            logger.error('Failed to add key')

def add_address(o_inst):
    try:
        newAddress = sys.argv[2]
        newAddress = newAddress.replace('http:', '').replace('/', '')
    except IndexError:
        pass
    else:
        logger.info("Adding address: " + logger.colors.underline + newAddress)
        if o_inst.onionrCore.addAddress(newAddress):
            logger.info("Successfully added address.")
        else:
            logger.warn("Unable to add address.")