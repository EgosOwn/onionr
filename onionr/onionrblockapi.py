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

import core as onionrcore, logger, config, onionrexceptions
import json, os, sys, datetime, base64

class Block:
    blockCacheOrder = list() # NEVER write your own code that writes to this!
    blockCache = dict() # should never be accessed directly, look at Block.getCache()

    def __init__(self, hash = None, core = None, type = None, content = None):
        # take from arguments
        # sometimes people input a bytes object instead of str in `hash`
        try:
            hash = hash.decode()
        except AttributeError:
            pass

        self.hash = hash
        self.core = core
        self.btype = type
        self.bcontent = content


        # initialize variables
        self.valid = True
        self.raw = None
        self.powHash = None
        self.powToken = None
        self.signed = False
        self.signature = None
        self.signedData = None
        self.blockFile = None
        self.parent = None
        self.bheader = {}
        self.bmetadata = {}

        # handle arguments
        if self.getCore() is None:
            self.core = onionrcore.Core()
        
        if not self.core._utils.validateHash(self.hash):
            raise onionrexceptions.InvalidHexHash('specified block hash is not valid')

        # update the blocks' contents if it exists
        if not self.getHash() is None:
            if not self.update():
                logger.debug('Failed to open block %s.' % self.getHash())
        else:
            logger.debug('Did not update block')

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

                readfile = True

                if filelocation is None:
                    if self.getHash() is None:
                        return False
                    elif self.getHash() in Block.getCache():
                        # get the block from cache, if it's in it
                        blockdata = Block.getCache(self.getHash())
                        readfile = False

                    # read from file if it's still None
                    if blockdata is None:
                        filelocation = 'data/blocks/%s.dat' % self.getHash()

                if readfile:
                    with open(filelocation, 'rb') as f:
                        blockdata = f.read().decode()

                self.blockFile = filelocation
            else:
                self.blockFile = None

            # parse block
            self.raw = str(blockdata)
            self.bheader = json.loads(self.getRaw()[:self.getRaw().index('\n')])
            self.bcontent = self.getRaw()[self.getRaw().index('\n') + 1:]
            self.bmetadata = json.loads(self.getHeader('meta', None))
            self.parent = self.getMetadata('parent', None)
            self.btype = self.getMetadata('type', None)
            self.powHash = self.getMetadata('powHash', None)
            self.powToken = self.getMetadata('powToken', None)
            self.signed = ('sig' in self.getHeader() and self.getHeader('sig') != '')
            self.signature = self.getHeader('sig', None)
            self.signedData = (None if not self.isSigned() else self.getHeader('meta') + '\n' + self.getContent())
            self.date = self.getCore().getBlockDate(self.getHash())

            if not self.getDate() is None:
                self.date = datetime.datetime.fromtimestamp(self.getDate())

            self.valid = True

            if len(self.getRaw()) <= config.get('allocations.blockCache', 500000):
                self.cache()

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
                return self.getHash()
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

    def getHeader(self, key = None, default = None):
        '''
            Returns the header information

            Inputs:
            - key (str): only returns the value of the key in the header

            Outputs:
            - (dict/str): either the whole header as a dict, or one value
        '''

        if not key is None:
            if key in self.getHeader():
                return self.getHeader()[key]
            return default
        return self.bheader

    def getMetadata(self, key = None, default = None):
        '''
            Returns the metadata information

            Inputs:
            - key (str): only returns the value of the key in the metadata

            Outputs:
            - (dict/str): either the whole metadata as a dict, or one value
        '''

        if not key is None:
            if key in self.getMetadata():
                return self.getMetadata()[key]
            return default
        return self.bmetadata

    def getContent(self):
        '''
            Returns the contents of the block

            Outputs:
            - (str): the contents of the block
        '''

        return str(self.bcontent)

    def getParent(self):
        '''
            Returns the Block's parent Block, or None

            Outputs:
            - (Block): the Block's parent
        '''

        if type(self.parent) == str:
            if self.parent == self.getHash():
                self.parent = self
            elif Block.exists(self.parent):
                self.parent = Block(self.getMetadata('parent'), core = self.getCore())
            else:
                self.parent = None

        return self.parent

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
            - (Block): the Block instance
        '''

        self.btype = btype
        return self

    def setMetadata(self, key, val):
        '''
            Sets a custom metadata value

            Metadata should not store block-specific data structures.

            Inputs:
            - key (str): the key
            - val: the value (type is irrelevant)

            Outputs:
            - (Block): the Block instance
        '''

        if key == 'parent' and (not val is None) and (not val == self.getParent().getHash()):
            self.setParent(val)
        else:
            self.bmetadata[key] = val
        return self

    def setContent(self, bcontent):
        '''
            Sets the contents of the block

            Inputs:
            - bcontent (str): the contents to be set to

            Outputs:
            - (Block): the Block instance
        '''

        self.bcontent = str(bcontent)
        return self

    def setParent(self, parent):
        '''
            Sets the Block's parent

            Inputs:
            - parent (Block/str): the Block's parent, to be stored in metadata

            Outputs:
            - (Block): the Block instance
        '''

        if type(parent) == str:
            parent = Block(parent, core = self.getCore())

        self.parent = parent
        self.setMetadata('parent', (None if parent is None else self.getParent().getHash()))
        return self

    # static functions

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

    def mergeChain(child, file = None, maximumFollows = 32, core = None):
        '''
            Follows a child Block to its root parent Block, merging content

            Inputs:
            - child (str/Block): the child Block to be followed
            - file (str/file): the file to write the content to, instead of returning it
            - maximumFollows (int): the maximum number of Blocks to follow
        '''

        # validate data and instantiate Core
        core = (core if not core is None else onionrcore.Core())
        maximumFollows = max(0, maximumFollows)

        # type conversions
        if type(child) == list:
            child = child[-1]
        if type(child) == str:
            child = Block(child)
        if (not file is None) and (type(file) == str):
            file = open(file, 'ab')

        # only store hashes to avoid intensive memory usage
        blocks = [child.getHash()]

        # generate a list of parent Blocks
        while True:
            # end if the maximum number of follows has been exceeded
            if len(blocks) - 1 >= maximumFollows:
                break

            block = Block(blocks[-1], core = core).getParent()

            # end if there is no parent Block
            if block is None:
                break

            # end if the Block is pointing to a previously parsed Block
            if block.getHash() in blocks:
                break

            # end if the block is not valid
            if not block.isValid():
                break

            blocks.append(block.getHash())

        buffer = ''

        # combine block contents
        for hash in blocks:
            block = Block(hash, core = core)
            contents = block.getContent()
            contents = base64.b64decode(contents.encode())

            if file is None:
                buffer += contents.decode()
            else:
                file.write(contents)

        return (None if not file is None else buffer)

    def createChain(data = None, chunksize = 99800, file = None, type = 'chunk', sign = True, encrypt = False, verbose = False):
        '''
            Creates a chain of blocks to store larger amounts of data

            The chunksize is set to 99800 because it provides the least amount of PoW for the most amount of data.

            Inputs:
            - data (*): if `file` is None, the data to be stored in blocks
            - file (file/str): the filename or file object to read from (or None to read `data` instead)
            - chunksize (int): the number of bytes per block chunk
            - type (str): the type header for each of the blocks
            - sign (bool): whether or not to sign each block
            - encrypt (str): the public key to encrypt to, or False to disable encryption
            - verbose (bool): whether or not to return a tuple containing more info

            Outputs:
            - if `verbose`:
              - (tuple):
                - (str): the child block hash
                - (list): all block hashes associated with storing the file
            - if not `verbose`:
              - (str): the child block hash
        '''

        blocks = list()

        # initial datatype checks
        if data is None and file is None:
            return blocks
        elif not (file is None or (isinstance(file, str) and os.path.exists(file))):
            return blocks
        elif isinstance(file, str):
            file = open(file, 'rb')
        if not isinstance(data, str):
            data = str(data)

        if not file is None:
            filesize = os.stat(file.name).st_size
            offset = filesize % chunksize
            maxtimes = int(filesize / chunksize)

            for times in range(0, maxtimes + 1):
                # read chunksize bytes from the file (end -> beginning)
                if times < maxtimes:
                    file.seek(- ((times + 1) * chunksize), 2)
                    content = file.read(chunksize)
                else:
                    file.seek(0, 0)
                    content = file.read(offset)

                # encode it- python is really bad at handling certain bytes that
                # are often present in binaries.
                content = base64.b64encode(content).decode()

                # if it is the end of the file, exit
                if not content:
                    break

                # create block
                block = Block()
                block.setType(type)
                block.setContent(content)
                block.setParent((blocks[-1] if len(blocks) != 0 else None))
                hash = block.save(sign = sign)

                # remember the hash in cache
                blocks.append(hash)
        elif not data is None:
            for content in reversed([data[n:n + chunksize] for n in range(0, len(data), chunksize)]):
                # encode chunk with base64
                content = base64.b64encode(content.encode()).decode()

                # create block
                block = Block()
                block.setType(type)
                block.setContent(content)
                block.setParent((blocks[-1] if len(blocks) != 0 else None))
                hash = block.save(sign = sign)

                # remember the hash in cache
                blocks.append(hash)

        # return different things depending on verbosity
        if verbose:
            return (blocks[-1], blocks)
        return blocks[-1]

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

        # no input data? scrap it.
        if hash is None:
            return False

        if type(hash) == Block:
            blockfile = hash.getBlockFile()
        else:
            blockfile = 'data/blocks/%s.dat' % hash

        return os.path.exists(blockfile) and os.path.isfile(blockfile)

    def getCache(hash = None):
        # give a list of the hashes of the cached blocks
        if hash is None:
            return list(Block.blockCache.keys())

        # if they inputted self or a Block, convert to hash
        if type(hash) == Block:
            hash = hash.getHash()

        # just to make sure someone didn't put in a bool or something lol
        hash = str(hash)

        # if it exists, return its content
        if hash in Block.getCache():
            return Block.blockCache[hash]

        return None

    def cache(block, override = False):
        # why even bother if they're giving bad data?
        if not type(block) == Block:
            return False

        # only cache if written to file
        if block.getHash() is None:
            return False

        # if it's already cached, what are we here for?
        if block.getHash() in Block.getCache() and not override:
            return False

        # dump old cached blocks if the size exeeds the maximum
        if sys.getsizeof(Block.blockCacheOrder) >= config.get('allocations.blockCacheTotal', 50000000): # 50MB default cache size
            del Block.blockCache[blockCacheOrder.pop(0)]

        # cache block content
        Block.blockCache[block.getHash()] = block.getRaw()
        Block.blockCacheOrder.append(block.getHash())

        return True
