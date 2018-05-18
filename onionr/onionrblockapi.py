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
        '''
            Initializes Onionr

            Inputs:
            - hash (str): the hash of the block to be imported, if any
            - core (Core/str):
              - if (Core): this is the Core instance to be used, don't create a new one
              - if (str): treat `core` as the block content, and instead, treat `hash` as the block type

            Outputs:
            - (Block): the new Block instance
        '''

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
        self.blockFile = None
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
        '''
            Deletes the block's file and records, if they exist

            Outputs:
            - (bool): whether or not the operation was successful
        '''

        if self.exists():
            os.remove(self.getBlockFile())
            removeBlock(self.getHash())
            return True
        return False

    def save(self, sign = False, recreate = True):
        '''
            Saves a block to file and imports it into Onionr

            Inputs:
            - sign (bool): whether or not to sign the block before saving
            - recreate (bool): if the block already exists, whether or not to recreate the block and save under a new hash

            Outputs:
            - (bool): whether or not the operation was successful
        '''

        try:
            if self.isValid() is True:
                if (not self.getBlockFile() is None) and (recreate is True):
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
        '''
            Returns the hash of the block if saved to file

            Outputs:
            - (str): the hash of the block, or None
        '''

        return self.hash

    def getCore(self):
        '''
            Returns the Core instance being used by the Block

            Outputs:
            - (Core): the Core instance
        '''

        return self.core

    def getType(self):
        '''
            Returns the type of the block

            Outputs:
            - (str): the type of the block
        '''

        return self.btype

    def getRaw(self):
        '''
            Returns the raw contents of the block, if saved to file

            Outputs:
            - (str): the raw contents of the block, or None
        '''

        return str(self.raw)

    def getHeader(self, key = None):
        '''
            Returns the header information

            Inputs:
            - key (str): only returns the value of the key in the header

            Outputs:
            - (dict/str): either the whole header as a dict, or one value
        '''

        if not key is None:
            return self.getHeader()[key]
        else:
            return self.bheader

    def getMetadata(self, key = None):
        '''
            Returns the metadata information

            Inputs:
            - key (str): only returns the value of the key in the metadata

            Outputs:
            - (dict/str): either the whole metadata as a dict, or one value
        '''

        if not key is None:
            return self.getMetadata()[key]
        else:
            return self.bmetadata

    def getContent(self):
        '''
            Returns the contents of the block

            Outputs:
            - (str): the contents of the block
        '''

        return str(self.bcontent)

    def getDate(self):
        '''
            Returns the date that the block was received, if loaded from file

            Outputs:
            - (datetime): the date that the block was received
        '''

        return self.date

    def getBlockFile(self):
        '''
            Returns the location of the block file if it is saved

            Outputs:
            - (str): the location of the block file, or None
        '''

        return self.blockFile

    def isValid(self):
        '''
            Checks if the block is valid

            Outputs:
            - (bool): whether or not the block is valid
        '''

        return self.valid

    def isSigned(self):
        '''
            Checks if the block was signed

            Outputs:
            - (bool): whether or not the block is signed
        '''

        return self.signed

    def getSignature(self):
        '''
            Returns the base64-encoded signature

            Outputs:
            - (str): the signature, or None
        '''

        return self.signature

    def getSignedData(self):
        '''
            Returns the data that was signed

            Outputs:
            - (str): the data that was signed, or None
        '''

        return self.signedData

    def isSigner(self, signer, encodedData = True):
        '''
            Checks if the block was signed by the signer inputted

            Inputs:
            - signer (str): the public key of the signer to check against
            - encodedData (bool): whether or not the `signer` argument is base64 encoded

            Outputs:
            - (bool): whether or not the signer of the block is the signer inputted
        '''

        try:
            if (not self.isSigned()) or (not self.getCore()._utils.validatePubKey(signer)):
                return False

            return bool(self.getCore()._crypto.edVerify(self.getSignedData(), signer, self.getSignature(), encodedData = encodedData))
        except:
            return False

    # setters

    def setType(self, btype):
        '''
            Sets the type of the block

            Inputs:
            - btype (str): the type of block to be set to

            Outputs:
            - (Block): the block instance
        '''

        self.btype = btype
        return self

    def setContent(self, bcontent):
        '''
            Sets the contents of the block

            Inputs:
            - bcontent (str): the contents to be set to

            Outputs:
            - (Block): the block instance
        '''

        self.bcontent = str(bcontent)
        return self

    # static

    def getBlocks(type = None, signer = None, signed = None, reverse = False, core = None):
        '''
            Returns a list of Block objects based on supplied filters

            Inputs:
            - type (str): filters by block type
            - signer (str/list): filters by signer (one in the list has to be a signer)
            - signed (bool): filters out by whether or not the block is signed
            - reverse (bool): reverses the list if True
            - core (Core): lets you optionally supply a core instance so one doesn't need to be started

            Outputs:
            - (list): a list of Block objects that match the input
        '''

        try:
            core = (core if not core is None else onionrcore.Core())

            relevant_blocks = list()
            blocks = (core.getBlockList() if type is None else core.getBlocksByType(type))

            for block in blocks:
                if Block.exists(block):
                    block = Block(block, core = core)

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

            if bool(reverse):
                relevant_blocks.reverse()

            return relevant_blocks
        except Exception as e:
            logger.debug(('Failed to get blocks: %s' % str(e)) + logger.parse_error())

        return list()

    def exists(hash):
        '''
            Checks if a block is saved to file or not

            Inputs:
            - hash (str/Block):
              - if (Block): check if this block is saved to file
              - if (str): check if a block by this hash is in file

            Outputs:
            - (bool): whether or not the block file exists
        '''

        if hash is None:
            return False
        elif type(hash) == Block:
            blockfile = hash.getBlockFile()
        else:
            blockfile = 'data/blocks/%s.dat' % hash

        return os.path.exists(blockfile) and os.path.isfile(blockfile)
