'''
    Onionr - Private P2P Communication

    Core Onionr library, useful for external programs. Handles peer & data processing
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
import os, sys, time, json, uuid
import logger, netcontroller, config
from onionrblockapi import Block
import coredb
import deadsimplekv as simplekv
import onionrutils, onionrcrypto, onionrproofs, onionrevents as events, onionrexceptions
import onionrblacklist
from onionrusers import onionrusers
from onionrstorage import removeblock, setdata
import dbcreator, onionrstorage, serializeddata, subprocesspow
from etc import onionrvalues, powchoice
from onionrutils import localcommand, stringvalidators, bytesconverter, epoch
from onionrutils import blockmetadata

class Core:
    def __init__(self, torPort=0):
        '''
            Initialize Core Onionr library
        '''
        # set data dir
        self.dataDir = os.environ.get('ONIONR_HOME', os.environ.get('DATA_DIR', 'data/'))
        if not self.dataDir.endswith('/'):
            self.dataDir += '/'

        try:
            self.onionrInst = None
            self.queueDB = self.dataDir + 'queue.db'
            self.peerDB = self.dataDir + 'peers.db'
            self.blockDB = self.dataDir + 'blocks.db'
            self.blockDataLocation = self.dataDir + 'blocks/'
            self.blockDataDB = self.blockDataLocation + 'block-data.db'
            self.publicApiHostFile = self.dataDir + 'public-host.txt'
            self.privateApiHostFile = self.dataDir + 'private-host.txt'
            self.addressDB = self.dataDir + 'address.db'
            self.hsAddress = ''
            self.i2pAddress = config.get('i2p.own_addr', None)
            self.bootstrapFileLocation = 'static-data/bootstrap-nodes.txt'
            self.bootstrapList = []
            self.requirements = onionrvalues.OnionrValues()
            self.torPort = torPort
            self.dataNonceFile = self.dataDir + 'block-nonces.dat'
            self.dbCreate = dbcreator.DBCreator(self)
            self.forwardKeysFile = self.dataDir + 'forward-keys.db'
            self.keyStore = simplekv.DeadSimpleKV(self.dataDir + 'cachedstorage.dat', refresh_seconds=5)
            
            # Socket data, defined here because of multithreading constraints with gevent
            self.killSockets = False
            self.startSocket = {}
            self.socketServerConnData = {}
            self.socketReasons = {}
            self.socketServerResponseData = {}

            self.usageFile = self.dataDir + 'disk-usage.txt'
            self.config = config

            self.maxBlockSize = 10000000 # max block size in bytes

            if not os.path.exists(self.dataDir):
                os.mkdir(self.dataDir)
            if not os.path.exists(self.dataDir + 'blocks/'):
                os.mkdir(self.dataDir + 'blocks/')
            if not os.path.exists(self.blockDB):
                self.createBlockDB()
            if not os.path.exists(self.forwardKeysFile):
                self.dbCreate.createForwardKeyDB()
            if not os.path.exists(self.peerDB):
                self.createPeerDB()
            if not os.path.exists(self.addressDB):
                self.createAddressDB()

            if os.path.exists(self.dataDir + '/hs/hostname'):
                with open(self.dataDir + '/hs/hostname', 'r') as hs:
                    self.hsAddress = hs.read().strip()

            # Load bootstrap address list
            if os.path.exists(self.bootstrapFileLocation):
                with open(self.bootstrapFileLocation, 'r') as bootstrap:
                    bootstrap = bootstrap.read()
                for i in bootstrap.split('\n'):
                    self.bootstrapList.append(i)
            else:
                logger.warn('Warning: address bootstrap file not found ' + self.bootstrapFileLocation)

            self.use_subprocess = powchoice.use_subprocess(self)
            self._utils = onionrutils.OnionrUtils(self)
            # Initialize the crypto object
            self._crypto = onionrcrypto.OnionrCrypto(self)
            self._blacklist = onionrblacklist.OnionrBlackList(self)
            self.serializer = serializeddata.SerializedData(self)

        except Exception as error:
            logger.error('Failed to initialize core Onionr library.', error=error)
            logger.fatal('Cannot recover from error.')
            sys.exit(1)
        return

    def refreshFirstStartVars(self):
        '''
            Hack to refresh some vars which may not be set on first start
        '''
        if os.path.exists(self.dataDir + '/hs/hostname'):
            with open(self.dataDir + '/hs/hostname', 'r') as hs:
                self.hsAddress = hs.read().strip()

    def addPeer(self, peerID, name=''):
        '''
            Adds a public key to the key database (misleading function name)
        '''
        return coredb.keydb.addkeys.add_peer(self, peerID, name)

    def addAddress(self, address):
        '''
            Add an address to the address database (only tor currently)
        '''
        return coredb.keydb.addkeys.add_address(self, address)

    def removeAddress(self, address):
        '''
            Remove an address from the address database
        '''
        return coredb.keydb.removekeys.remove_address(self, address)

    def removeBlock(self, block):
        '''
            remove a block from this node (does not automatically blacklist)

            **You may want blacklist.addToDB(blockHash)
        '''
        removeblock.remove_block(self, block)

    def createAddressDB(self):
        '''
            Generate the address database
        '''
        self.dbCreate.createAddressDB()

    def createPeerDB(self):
        '''
            Generate the peer sqlite3 database and populate it with the peers table.
        '''
        self.dbCreate.createPeerDB()

    def createBlockDB(self):
        '''
            Create a database for blocks
        '''
        self.dbCreate.createBlockDB()

    def addToBlockDB(self, newHash, selfInsert=False, dataSaved=False):
        '''
            Add a hash value to the block db

            Should be in hex format!
        '''
        coredb.blockmetadb.add.add_to_block_DB(self, newHash, selfInsert, dataSaved)

    def setData(self, data):
        '''
            Set the data assciated with a hash
        '''
        return onionrstorage.setdata.set_data(self, data)

    def getData(self, hash):
        '''
            Simply return the data associated to a hash
        '''
        return onionrstorage.getData(self, hash)

    def daemonQueue(self):
        '''
            Gives commands to the communication proccess/daemon by reading an sqlite3 database

            This function intended to be used by the client. Queue to exchange data between "client" and server.
        '''
        return coredb.daemonqueue.daemon_queue(self)

    def daemonQueueAdd(self, command, data='', responseID=''):
        '''
            Add a command to the daemon queue, used by the communication daemon (communicator.py)
        '''
        return coredb.daemonqueue.daemon_queue_add(self, command, data, responseID)

    def daemonQueueGetResponse(self, responseID=''):
        '''
            Get a response sent by communicator to the API, by requesting to the API
        '''
        return coredb.daemonqueue.daemon_queue_get_response(self, responseID)

    def clearDaemonQueue(self):
        '''
            Clear the daemon queue (somewhat dangerous)
        '''
        return coredb.daemonqueue.clear_daemon_queue(self)

    def listAdders(self, randomOrder=True, i2p=True, recent=0):
        '''
            Return a list of addresses
        '''
        return coredb.keydb.listkeys.list_adders(self, randomOrder, i2p, recent)

    def listPeers(self, randomOrder=True, getPow=False, trust=0):
        '''
            Return a list of public keys (misleading function name)

            randomOrder determines if the list should be in a random order
            trust sets the minimum trust to list
        '''
        return coredb.keydb.listkeys.list_peers(self, randomOrder, getPow, trust)

    def getPeerInfo(self, peer, info):
        '''
            Get info about a peer from their database entry

            id text             0
            name text,          1
            adders text,        2
            dateSeen not null,  3
            trust int           4
            hashID text         5
        '''
        return coredb.keydb.userinfo.get_user_info(self, peer, info)

    def setPeerInfo(self, peer, key, data):
        '''
            Update a peer for a key
        '''
        return coredb.keydb.userinfo.set_peer_info(self, peer, key, data)

    def getAddressInfo(self, address, info):
        '''
            Get info about an address from its database entry

            address text, 0
            type int, 1
            knownPeer text, 2
            speed int, 3
            success int, 4
            powValue    5
            failure int 6
            lastConnect 7
            trust       8
            introduced  9
        '''
        return coredb.keydb.transportinfo.get_address_info(self, address, info)

    def setAddressInfo(self, address, key, data):
        '''
            Update an address for a key
        '''
        return coredb.keydb.transportinfo.set_address_info(self, address, key, data)

    def getBlockList(self, dateRec = None, unsaved = False):
        '''
            Get list of our blocks
        '''
        return coredb.blockmetadb.get_block_list(self, dateRec, unsaved)

    def getBlockDate(self, blockHash):
        '''
            Returns the date a block was received
        '''
        return coredb.blockmetadb.get_block_date(self, blockHash)

    def getBlocksByType(self, blockType, orderDate=True):
        '''
            Returns a list of blocks by the type
        '''
        return coredb.blockmetadb.get_blocks_by_type(self, blockType, orderDate)

    def getExpiredBlocks(self):
        '''Returns a list of expired blocks'''
        return coredb.blockmetadb.expiredblocks.get_expired_blocks(self)

    def updateBlockInfo(self, hash, key, data):
        '''
            sets info associated with a block

            hash         - the hash of a block
            dateReceived - the date the block was recieved, not necessarily when it was created
            decrypted    - if we can successfully decrypt the block (does not describe its current state)
            dataType     - data type of the block
            dataFound    - if the data has been found for the block
            dataSaved    - if the data has been saved for the block
            sig    - optional signature by the author (not optional if author is specified)
            author       - multi-round partial sha3-256 hash of authors public key
            dateClaimed  - timestamp claimed inside the block, only as trustworthy as the block author is
            expire       - expire date for a block
        '''
        return coredb.blockmetadb.updateblockinfo

    def insertBlock(self, data, header='txt', sign=False, encryptType='', symKey='', asymPeer='', meta = {}, expire=None, disableForward=False):
        '''
            Inserts a block into the network
            encryptType must be specified to encrypt a block
        '''
        allocationReachedMessage = 'Cannot insert block, disk allocation reached.'
        if self._utils.storageCounter.isFull():
            logger.error(allocationReachedMessage)
            return False
        retData = False

        if type(data) is None:
            raise ValueError('Data cannot be none')

        createTime = epoch.get_epoch()

        dataNonce = bytesconverter.bytes_to_str(self._crypto.sha3Hash(data))
        try:
            with open(self.dataNonceFile, 'r') as nonces:
                if dataNonce in nonces:
                    return retData
        except FileNotFoundError:
            pass
        # record nonce
        with open(self.dataNonceFile, 'a') as nonceFile:
            nonceFile.write(dataNonce + '\n')

        if type(data) is bytes:
            data = data.decode()
        data = str(data)
        plaintext = data
        plaintextMeta = {}
        plaintextPeer = asymPeer

        retData = ''
        signature = ''
        signer = ''
        metadata = {}
        # metadata is full block metadata, meta is internal, user specified metadata

        # only use header if not set in provided meta

        meta['type'] = str(header)

        if encryptType in ('asym', 'sym', ''):
            metadata['encryptType'] = encryptType
        else:
            raise onionrexceptions.InvalidMetadata('encryptType must be asym or sym, or blank')

        try:
            data = data.encode()
        except AttributeError:
            pass

        if encryptType == 'asym':
            meta['rply'] = createTime # Duplicate the time in encrypted messages to prevent replays
            if not disableForward and sign and asymPeer != self._crypto.pubKey:
                try:
                    forwardEncrypted = onionrusers.OnionrUser(self, asymPeer).forwardEncrypt(data)
                    data = forwardEncrypted[0]
                    meta['forwardEnc'] = True
                    expire = forwardEncrypted[2] # Expire time of key. no sense keeping block after that
                except onionrexceptions.InvalidPubkey:
                    pass
                    #onionrusers.OnionrUser(self, asymPeer).generateForwardKey()
                fsKey = onionrusers.OnionrUser(self, asymPeer).generateForwardKey()
                #fsKey = onionrusers.OnionrUser(self, asymPeer).getGeneratedForwardKeys().reverse()
                meta['newFSKey'] = fsKey
        jsonMeta = json.dumps(meta)
        plaintextMeta = jsonMeta
        if sign:
            signature = self._crypto.edSign(jsonMeta.encode() + data, key=self._crypto.privKey, encodeResult=True)
            signer = self._crypto.pubKey

        if len(jsonMeta) > 1000:
            raise onionrexceptions.InvalidMetadata('meta in json encoded form must not exceed 1000 bytes')

        user = onionrusers.OnionrUser(self, symKey)

        # encrypt block metadata/sig/content
        if encryptType == 'sym':

            if len(symKey) < self.requirements.passwordLength:
                raise onionrexceptions.SecurityError('Weak encryption key')
            jsonMeta = self._crypto.symmetricEncrypt(jsonMeta, key=symKey, returnEncoded=True).decode()
            data = self._crypto.symmetricEncrypt(data, key=symKey, returnEncoded=True).decode()
            signature = self._crypto.symmetricEncrypt(signature, key=symKey, returnEncoded=True).decode()
            signer = self._crypto.symmetricEncrypt(signer, key=symKey, returnEncoded=True).decode()
        elif encryptType == 'asym':
            if stringvalidators.validate_pub_key(asymPeer):
                # Encrypt block data with forward secrecy key first, but not meta
                jsonMeta = json.dumps(meta)
                jsonMeta = self._crypto.pubKeyEncrypt(jsonMeta, asymPeer, encodedData=True).decode()
                data = self._crypto.pubKeyEncrypt(data, asymPeer, encodedData=True).decode()
                signature = self._crypto.pubKeyEncrypt(signature, asymPeer, encodedData=True).decode()
                signer = self._crypto.pubKeyEncrypt(signer, asymPeer, encodedData=True).decode()
                try:
                    onionrusers.OnionrUser(self, asymPeer, saveUser=True)
                except ValueError:
                    # if peer is already known
                    pass
            else:
                raise onionrexceptions.InvalidPubkey(asymPeer + ' is not a valid base32 encoded ed25519 key')

        # compile metadata
        metadata['meta'] = jsonMeta
        metadata['sig'] = signature
        metadata['signer'] = signer
        metadata['time'] = createTime

        # ensure expire is integer and of sane length
        if type(expire) is not type(None):
            assert len(str(int(expire))) < 14
            metadata['expire'] = expire

        # send block data (and metadata) to POW module to get tokenized block data
        if self.use_subprocess:
            payload = subprocesspow.SubprocessPOW(data, metadata, self).start()
        else:
            payload = onionrproofs.POW(metadata, data).waitForResult()
        if payload != False:
            try:
                retData = self.setData(payload)
            except onionrexceptions.DiskAllocationReached:
                logger.error(allocationReachedMessage)
                retData = False
            else:
                # Tell the api server through localCommand to wait for the daemon to upload this block to make statistical analysis more difficult
                if localcommand.local_command(self, '/ping', maxWait=10) == 'pong!':
                    localcommand.local_command(self, '/waitforshare/' + retData, post=True, maxWait=5)
                    self.daemonQueueAdd('uploadBlock', retData)
                self.addToBlockDB(retData, selfInsert=True, dataSaved=True)
                blockmetadata.process_block_metadata(retData)

        if retData != False:
            if plaintextPeer == onionrvalues.DENIABLE_PEER_ADDRESS:
                events.event('insertdeniable', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': bytesconverter.bytes_to_str(asymPeer)}, onionr = self.onionrInst, threaded = True)
            else:
                events.event('insertblock', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': bytesconverter.bytes_to_str(asymPeer)}, onionr = self.onionrInst, threaded = True)
        return retData

    def introduceNode(self):
        '''
            Introduces our node into the network by telling X many nodes our HS address
        '''
        if localcommand.local_command(self, '/ping', maxWait=10) == 'pong!':
            self.daemonQueueAdd('announceNode')
            logger.info('Introduction command will be processed.', terminal=True)
        else:
            logger.warn('No running node detected. Cannot introduce.', terminal=True)