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
def mergeAdders(newAdderList, coreInst):
    '''
        Merge peer adders list to our database
    '''
    try:
        retVal = False
        if newAdderList != False:
            for adder in newAdderList.split(','):
                adder = adder.strip()
                if not adder in coreInst.listAdders(randomOrder = False) and adder != coreInst.hsAddress and not coreInst._blacklist.inBlacklist(adder):
                    if not config.get('tor.v3onions') and len(adder) == 62:
                        continue
                    if coreInst.addAddress(adder):
                        # Check if we have the maxmium amount of allowed stored peers
                        if config.get('peers.max_stored_peers') > len(coreInst.listAdders()):
                            logger.info('Added %s to db.' % adder, timestamp = True)
                            retVal = True
                        else:
                            logger.warn('Reached the maximum amount of peers in the net database as allowed by your config.')
                else:
                    pass
                    #logger.debug('%s is either our address or already in our DB' % adder)
        return retVal
    except Exception as error:
        logger.error('Failed to merge adders.', error = error)
        return False