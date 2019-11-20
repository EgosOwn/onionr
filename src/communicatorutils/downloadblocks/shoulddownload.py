'''
    Onionr - Private P2P Communication

    Check if a block should be downloaded (if we already have it or its blacklisted or not)
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
from coredb import blockmetadb
from onionrblocks import onionrblacklist

def should_download(comm_inst, block_hash):
    blacklist = onionrblacklist.OnionrBlackList()
    ret_data = True
    if block_hash in blockmetadb.get_block_list(): # Dont download block we have
        ret_data = False
    else:
        if blacklist.inBlacklist(block_hash): # Dont download blacklisted block
            ret_data = False
    if ret_data is False:
        # Remove block from communicator queue if it shouldnt be downloaded
        try:
            del comm_inst.blockQueue[block_hash]
        except KeyError:
            pass
    return ret_data