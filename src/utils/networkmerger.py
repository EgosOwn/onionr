'''
    Onionr - P2P Microblogging Platform & Social network

    Merges peer and block lists
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
import logger
from coredb import keydb
import config
from onionrblocks import onionrblacklist
from utils import gettransports
def mergeAdders(newAdderList):
    '''
        Merge peer adders list to our database
    '''
    blacklist = onionrblacklist.OnionrBlackList()
    retVal = False
    if newAdderList != False:
        for adder in newAdderList.split(','):
            adder = adder.strip()
            if not adder in keydb.listkeys.list_adders(randomOrder = False) and not adder in gettransports.get() and not blacklist.inBlacklist(adder):
                if keydb.addkeys.add_address(adder):
                    # Check if we have the maximum amount of allowed stored peers
                    if config.get('peers.max_stored_peers') > len(keydb.listkeys.list_adders()):
                        logger.info('Added %s to db.' % adder, timestamp = True)
                        retVal = True
                    else:
                        logger.warn('Reached the maximum amount of peers in the net database as allowed by your config.')
            else:
                pass
                #logger.debug('%s is either our address or already in our DB' % adder)
    return retVal
