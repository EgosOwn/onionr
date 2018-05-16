'''
    Onionr - P2P Microblogging Platform & Social network.

    This class contains the OnionrBlocks class which is a class for working with Onionr blocks
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

import core as onionrcore, logger
import json, os, datetime

class Block:
    def __init__(self, hash = None, core = None):
        # input from arguments
        if (type(hash) == str) and (type(core) == str):
            self.btype = hash
            self.bcontent = core
            self.hash = None
            self.core = None
        else:
            self.btype = ''
            self.bcontent = ''
            self.hash = hash
            self.core = core

        # initialize variables
        self.valid = True
        self.raw = None
        self.powHash = None
        self.powToken = None
        self.signed = False
        self.signature = None
        self.signedData = None
        self.bheader = {}
        self.bmetadata = {}

        # handle arguments
        if self.getCore() is None:
            self.core = onionrcore.Core()
        if not self.getHash() is None:
            self.update()

    # logic

    def update(self, data = None, file = None):
        '''
            Loads data from a block in to the current object.

            Inputs:
            - data (str):
              - if None: will load from file by hash
              - else: will load from `data` string
            - file (str):
              - if None: will load from file specified in this parameter
              - else: will load from wherever block is stored by hash

            Outputs:
            - (bool): indicates whether or not the operation was successful
        '''

        try:
            # import from string
            blockdata = data

            # import from file
            if blockdata is None:
                filelocation = file

                if filelocation is None:
                    if self.getHash() is None:
                        return False

                    filelocation = 'data/blocks/%s.dat' % self.getHash()

                blockdata = open(filelocation, 'rb').read().decode('utf-8')

                self.blockFile = filelocation
            else:
                self.blockFile = None

            # parse block
            self.raw = str(blockdata)
            self.bheader = json.loads(self.getRaw()[:self.getRaw().index('\n')])
            self.bcontent = self.getRaw()[self.getRaw().index('\n') + 1:]
            self.bmetadata = json.loads(self.getHeader('meta'))
            self.btype = self.getMetadata('type')
            self.powHash = self.getMetadata('powHash')
            self.powToken = self.getMetadata('powToken')
            self.signed = ('sig' in self.getHeader() and self.getHeader('sig') != '')
            self.signature = (None if not self.isSigned() else self.getHeader('sig'))
            self.signedData = (None if not self.isSigned() else self.getHeader('meta') + '\n' + self.getContent())
            self.date = self.getCore().getBlockDate(self.getHash())

            if not self.getDate() is None:
                self.date = datetime.datetime.fromtimestamp(self.getDate())

            self.valid = True
            return True
        except Exception as e:
            logger.error('Failed to update block data.', error = e, timestamp = False)

        self.valid = False
        return False

    def delete(self):
        if self.exists():
            os.remove(self.getBlockFile())
            return True
        return False

    def save(self, sign = False, recreate = False):
        try:
            if self.isValid() is True:
                if (recreate is True) and (not self.getBlockFile() is None):
                    with open(self.getBlockFile(), 'wb') as blockFile:
                        blockFile.write(self.getRaw().encode())
                    self.update()
                else:
                    self.hash = self.getCore().insertBlock(self.getContent(), header = self.getType(), sign = sign)
                    self.update()
                return True
            else:
                logger.warn('Not writing block; it is invalid.')
        except Exception as e:
            logger.error('Failed to save block.', error = e, timestamp = False)
            return False

    # getters

    def getHash(self):
        return self.hash

    def getCore(self):
        return self.core

    def getType(self):
        return self.btype

    def getRaw(self):
        return str(self.raw)

    def getHeader(self, key = None):
        if not key is None:
            return self.getHeader()[key]
        else:
            return self.bheader

    def getMetadata(self, key = None):
        if not key is None:
            return self.getMetadata()[key]
        else:
            return self.bmetadata

    def getContent(self):
        return str(self.bcontent)

    def getDate(self):
        return self.date

    def getBlockFile(self):
        return self.blockFile

    def isValid(self):
        return self.valid

    def isSigned(self):
        return self.signed

    def getSignature(self):
        return self.signature

    def getSignedData(self):
        return self.signedData

    def isSigner(self, signer, encodedData = True):
        try:
            if (not self.isSigned()) or (not self.getCore()._utils.validatePubKey(signer)):
                return False

            return bool(self.getCore()._crypto.edVerify(self.getSignedData(), signer, self.getSignature(), encodedData = encodedData))
        except:
            return False

    # setters

    def setType(self, btype):
        self.btype = btype
        return self

    def setContent(self, bcontent):
        self.bcontent = str(bcontent)
        return self

    # static

    ORDER_DATE = 0
    ORDER_ALPHABETIC = 1

    def getBlocks(type = None, signer = None, signed = None, order = ORDER_DATE, reverse = False, core = None):
        try:
            core = (core if not core is None else onionrcore.Core())

            relevant_blocks = list()
            blocks = (core.getBlockList() if type is None else core.getBlocksByType(type))

            for block in blocks:
                if Block.exists(block):
                    block = Block(block)

                    relevant = True

                    if (not signed is None) and (block.isSigned() != bool(signed)):
                        relevant = False
                    if not signer is None:
                        if isinstance(signer, (str,)):
                            signer = [signer]

                        isSigner = False
                        for key in signer:
                            if block.isSigner(key):
                                isSigner = True
                                break

                        if not isSigner:
                            relevant = False

                    if relevant:
                        relevant_blocks.append(block)

            return relevant_blocks
        except Exception as e:
            logger.debug(('Failed to get blocks: %s' % str(e)) + logger.parse_error())

        return list()

    def exists(hash):
        if hash is None:
            return False
        elif type(hash) == Block:
            blockfile = hash.getBlockFile()
        else:
            blockfile = 'data/blocks/%s.dat' % hash

        return os.path.exists(blockfile) and os.path.isfile(blockfile)
