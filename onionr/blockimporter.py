'''
    Onionr - P2P Microblogging Platform & Social network

    Import block data and save it
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
import core, onionrexceptions, logger
def importBlockFromData(content, coreInst):
    retData = False

    dataHash = coreInst._getSha3Hash(content)

    if coreInst._blacklist.inBlacklist(dataHash):
        raise onionrexceptions.BlacklistedBlock('%s is a blacklisted block' % (dataHash,))

    if not isinstance(coreInst, core.Core):
        raise Exception("coreInst must be an Onionr core instance")

    try:
        content = content.encode()
    except AttributeError:
        pass

    metas = coreInst._utils.getBlockMetadataFromData(content) # returns tuple(metadata, meta), meta is also in metadata
    metadata = metas[0]
    if coreInst._utils.validateMetadata(metadata, metas[2]): # check if metadata is valid
        if coreInst._crypto.verifyPow(content): # check if POW is enough/correct
            logger.info('Block passed proof, saving.')
            blockHash = coreInst.setData(content)
            blockHash = coreInst.addToBlockDB(blockHash, dataSaved=True)
            coreInst._utils.processBlockMetadata(blockHash) # caches block metadata values to block database
            retData = True
    return retData