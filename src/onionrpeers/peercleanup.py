'''
    Onionr - Private P2P Communication

    Cleanup the peer database
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
import sqlite3
import logger
from onionrutils import epoch
from . import scoresortedpeerlist, peerprofiles
from onionrblocks import onionrblacklist
import config
from coredb import keydb
def peer_cleanup():
    '''Removes peers who have been offline too long or score too low'''
    logger.info('Cleaning peers...')
    blacklist = onionrblacklist.OnionrBlackList()
    adders = scoresortedpeerlist.get_score_sorted_peer_list()
    adders.reverse()
    
    if len(adders) > 1:

        min_score = int(config.get('peers.minimum_score', -100))
        max_peers = int(config.get('peers.max_stored', 5000))

        for address in adders:
            # Remove peers that go below the negative score
            if peerprofiles.PeerProfiles(address).score < min_score:
                keydb.removekeys.remove_address(address)
                try:
                    lastConnect = int(keydb.transportinfo.get_address_info(address, 'lastConnect'))
                    expireTime = 86400 - int(epoch.get_epoch()) - lastConnect
                    blacklist.addToDB(address, dataType=1, expire=expireTime)
                except sqlite3.IntegrityError: #TODO just make sure its not a unique constraint issue
                    pass
                except ValueError:
                    pass
                logger.warn('Removed address ' + address + '.')

    # Unban probably not malicious peers TODO improve
    blacklist.deleteExpired(dataType=1)