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
import sqlite3, os, sys, time, json, uuid
import logger, netcontroller, config
from onionrblockapi import Block
import deadsimplekv as simplekv
import onionrutils, onionrcrypto, onionrproofs, onionrevents as events, onionrexceptions
import onionrblacklist
from onionrusers import onionrusers
import dbcreator, onionrstorage, serializeddata, subprocesspow
from etc import onionrvalues, powchoice

if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        logger.fatal('On Python 3 versions prior to 3.6.x, you need the sha3 module')
        sys.exit(1)

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
        if peerID in self.listPeers() or peerID == self._crypto.pubKey:
            raise ValueError("specified id is already known")

        # This function simply adds a peer to the DB
        if not self._utils.validatePubKey(peerID):
            return False

        events.event('pubkey_add', data = {'key': peerID}, onionr = self.onionrInst)

        conn = sqlite3.connect(self.peerDB, timeout=30)
        hashID = self._crypto.pubKeyHashID(peerID)
        c = conn.cursor()
        t = (peerID, name, 'unknown', hashID, 0)

        for i in c.execute("SELECT * FROM peers WHERE id = ?;", (peerID,)):
            try:
                if i[0] == peerID:
                    conn.close()
                    return False
            except ValueError:
                pass
            except IndexError:
                pass
        c.execute('INSERT INTO peers (id, name, dateSeen, hashID, trust) VALUES(?, ?, ?, ?, ?);', t)
        conn.commit()
        conn.close()

        return True

    def addAddress(self, address):
        '''
            Add an address to the address database (only tor currently)
        '''

        if type(address) is None or len(address) == 0:
            return False
        if self._utils.validateID(address):
            if address == config.get('i2p.ownAddr', None) or address == self.hsAddress:
                return False
            conn = sqlite3.connect(self.addressDB, timeout=30)
            c = conn.cursor()
            # check if address is in database
            # this is safe to do because the address is validated above, but we strip some chars here too just in case
            address = address.replace('\'', '').replace(';', '').replace('"', '').replace('\\', '')
            for i in c.execute("SELECT * FROM adders WHERE address = ?;", (address,)):
                try:
                    if i[0] == address:
                        conn.close()
                        return False
                except ValueError:
                    pass
                except IndexError:
                    pass

            t = (address, 1)
            c.execute('INSERT INTO adders (address, type) VALUES(?, ?);', t)
            conn.commit()
            conn.close()

            events.event('address_add', data = {'address': address}, onionr = self.onionrInst)

            return True
        else:
            #logger.debug('Invalid ID: %s' % address)
            return False

    def removeAddress(self, address):
        '''
            Remove an address from the address database
        '''

        if self._utils.validateID(address):
            conn = sqlite3.connect(self.addressDB, timeout=30)
            c = conn.cursor()
            t = (address,)
            c.execute('Delete from adders where address=?;', t)
            conn.commit()
            conn.close()

            events.event('address_remove', data = {'address': address}, onionr = self.onionrInst)
            return True
        else:
            return False

    def removeBlock(self, block):
        '''
            remove a block from this node (does not automatically blacklist)

            **You may want blacklist.addToDB(blockHash)
        '''

        if self._utils.validateHash(block):
            conn = sqlite3.connect(self.blockDB, timeout=30)
            c = conn.cursor()
            t = (block,)
            c.execute('Delete from hashes where hash=?;', t)
            conn.commit()
            conn.close()
            dataSize = sys.getsizeof(onionrstorage.getData(self, block))
            self._utils.storageCounter.removeBytes(dataSize)
        else:
            raise onionrexceptions.InvalidHexHash

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

        if not os.path.exists(self.blockDB):
            raise Exception('Block db does not exist')
        if self._utils.hasBlock(newHash):
            return
        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()
        currentTime = self._utils.getEpoch() + self._crypto.secrets.randbelow(301)
        if selfInsert or dataSaved:
            selfInsert = 1
        else:
            selfInsert = 0
        data = (newHash, currentTime, '', selfInsert)
        c.execute('INSERT INTO hashes (hash, dateReceived, dataType, dataSaved) VALUES(?, ?, ?, ?);', data)
        conn.commit()
        conn.close()

        return

    def getData(self, hash):
        '''
            Simply return the data associated to a hash
        '''

        data = onionrstorage.getData(self, hash)

        return data

    def setData(self, data):
        '''
            Set the data assciated with a hash
        '''

        data = data
        dataSize = sys.getsizeof(data)

        if not type(data) is bytes:
            data = data.encode()

        dataHash = self._crypto.sha3Hash(data)

        if type(dataHash) is bytes:
            dataHash = dataHash.decode()
        blockFileName = self.blockDataLocation + dataHash + '.dat'
        if os.path.exists(blockFileName):
            pass # TODO: properly check if block is already saved elsewhere
            #raise Exception("Data is already set for " + dataHash)
        else:
            if self._utils.storageCounter.addBytes(dataSize) != False:
                onionrstorage.store(self, data, blockHash=dataHash)
                conn = sqlite3.connect(self.blockDB, timeout=30)
                c = conn.cursor()
                c.execute("UPDATE hashes SET dataSaved=1 WHERE hash = ?;", (dataHash,))
                conn.commit()
                conn.close()
                with open(self.dataNonceFile, 'a') as nonceFile:
                    nonceFile.write(dataHash + '\n')
            else:
                raise onionrexceptions.DiskAllocationReached

        return dataHash

    def daemonQueue(self):
        '''
            Gives commands to the communication proccess/daemon by reading an sqlite3 database

            This function intended to be used by the client. Queue to exchange data between "client" and server.
        '''

        retData = False
        if not os.path.exists(self.queueDB):
            self.dbCreate.createDaemonDB()
        else:
            conn = sqlite3.connect(self.queueDB, timeout=30)
            c = conn.cursor()
            try:
                for row in c.execute('SELECT command, data, date, min(ID), responseID FROM commands group by id'):
                    retData = row
                    break
            except sqlite3.OperationalError:
                self.dbCreate.createDaemonDB()
            else:
                if retData != False:
                    c.execute('DELETE FROM commands WHERE id=?;', (retData[3],))
            conn.commit()
            conn.close()

        events.event('queue_pop', data = {'data': retData}, onionr = self.onionrInst)

        return retData

    def daemonQueueAdd(self, command, data='', responseID=''):
        '''
            Add a command to the daemon queue, used by the communication daemon (communicator.py)
        '''

        retData = True

        date = self._utils.getEpoch()
        conn = sqlite3.connect(self.queueDB, timeout=30)
        c = conn.cursor()
        t = (command, data, date, responseID)
        try:
            c.execute('INSERT INTO commands (command, data, date, responseID) VALUES(?, ?, ?, ?)', t)
            conn.commit()
        except sqlite3.OperationalError:
            retData = False
            self.daemonQueue()
        events.event('queue_push', data = {'command': command, 'data': data}, onionr = self.onionrInst)
        conn.close()
        return retData

    def daemonQueueGetResponse(self, responseID=''):
        '''
            Get a response sent by communicator to the API, by requesting to the API
        '''
        assert len(responseID) > 0
        resp = self._utils.localCommand('queueResponse/' + responseID)
        return resp

    def daemonQueueWaitForResponse(self, responseID='', checkFreqSecs=1):
        resp = 'failure'
        while resp == 'failure':
            resp = self.daemonQueueGetResponse(responseID)
            time.sleep(1)
        return resp

    def daemonQueueSimple(self, command, data='', checkFreqSecs=1):
        '''
        A simplified way to use the daemon queue. Will register a command (with optional data) and wait, return the data
        Not always useful, but saves time + LOC in some cases.
        This is a blocking function, so be careful.
        '''
        responseID = str(uuid.uuid4()) # generate unique response ID
        self.daemonQueueAdd(command, data=data, responseID=responseID)
        return self.daemonQueueWaitForResponse(responseID, checkFreqSecs)

    def clearDaemonQueue(self):
        '''
            Clear the daemon queue (somewhat dangerous)
        '''
        conn = sqlite3.connect(self.queueDB, timeout=30)
        c = conn.cursor()

        try:
            c.execute('DELETE FROM commands;')
            conn.commit()
        except:
            pass

        conn.close()
        events.event('queue_clear', onionr = self.onionrInst)

        return

    def listAdders(self, randomOrder=True, i2p=True, recent=0):
        '''
            Return a list of addresses
        '''
        conn = sqlite3.connect(self.addressDB, timeout=30)
        c = conn.cursor()
        if randomOrder:
            addresses = c.execute('SELECT * FROM adders ORDER BY RANDOM();')
        else:
            addresses = c.execute('SELECT * FROM adders;')
        addressList = []
        for i in addresses:
            if len(i[0].strip()) == 0:
                continue
            addressList.append(i[0])
        conn.close()
        testList = list(addressList) # create new list to iterate
        for address in testList:
            try:
                if recent > 0 and (self._utils.getEpoch() - self.getAddressInfo(address, 'lastConnect')) > recent:
                    raise TypeError # If there is no last-connected date or it was too long ago, don't add peer to list if recent is not 0
            except TypeError:
                addressList.remove(address)
        return addressList

    def listPeers(self, randomOrder=True, getPow=False, trust=0):
        '''
            Return a list of public keys (misleading function name)

            randomOrder determines if the list should be in a random order
            trust sets the minimum trust to list
        '''
        conn = sqlite3.connect(self.peerDB, timeout=30)
        c = conn.cursor()

        payload = ''

        if trust not in (0, 1, 2):
            logger.error('Tried to select invalid trust.')
            return

        if randomOrder:
            payload = 'SELECT * FROM peers WHERE trust >= ? ORDER BY RANDOM();'
        else:
            payload = 'SELECT * FROM peers WHERE trust >= ?;'

        peerList = []

        for i in c.execute(payload, (trust,)):
            try:
                if len(i[0]) != 0:
                    if getPow:
                        peerList.append(i[0] + '-' + i[1])
                    else:
                        peerList.append(i[0])
            except TypeError:
                pass

        conn.close()

        return peerList

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
        conn = sqlite3.connect(self.peerDB, timeout=30)
        c = conn.cursor()

        command = (peer,)
        infoNumbers = {'id': 0, 'name': 1, 'adders': 2, 'dateSeen': 3, 'trust': 4, 'hashID': 5}
        info = infoNumbers[info]
        iterCount = 0
        retVal = ''

        for row in c.execute('SELECT * FROM peers WHERE id=?;', command):
            for i in row:
                if iterCount == info:
                    retVal = i
                    break
                else:
                    iterCount += 1

        conn.close()

        return retVal

    def setPeerInfo(self, peer, key, data):
        '''
            Update a peer for a key
        '''

        conn = sqlite3.connect(self.peerDB, timeout=30)
        c = conn.cursor()

        command = (data, peer)

        # TODO: validate key on whitelist
        if key not in ('id', 'name', 'pubkey', 'forwardKey', 'dateSeen', 'trust'):
            raise Exception("Got invalid database key when setting peer info")

        c.execute('UPDATE peers SET ' + key + ' = ? WHERE id=?', command)
        conn.commit()
        conn.close()

        return

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

        conn = sqlite3.connect(self.addressDB, timeout=30)
        c = conn.cursor()

        command = (address,)
        infoNumbers = {'address': 0, 'type': 1, 'knownPeer': 2, 'speed': 3, 'success': 4, 'powValue': 5, 'failure': 6, 'lastConnect': 7, 'trust': 8, 'introduced': 9}
        info = infoNumbers[info]
        iterCount = 0
        retVal = ''

        for row in c.execute('SELECT * FROM adders WHERE address=?;', command):
            for i in row:
                if iterCount == info:
                    retVal = i
                    break
                else:
                    iterCount += 1
        conn.close()

        return retVal

    def setAddressInfo(self, address, key, data):
        '''
            Update an address for a key
        '''

        conn = sqlite3.connect(self.addressDB, timeout=30)
        c = conn.cursor()

        command = (data, address)

        if key not in ('address', 'type', 'knownPeer', 'speed', 'success', 'failure', 'powValue', 'lastConnect', 'lastConnectAttempt', 'trust', 'introduced'):
            raise Exception("Got invalid database key when setting address info")
        else:
            c.execute('UPDATE adders SET ' + key + ' = ? WHERE address=?', command)
            conn.commit()
        conn.close()

        return

    def getBlockList(self, dateRec = None, unsaved = False):
        '''
            Get list of our blocks
        '''
        if dateRec == None:
            dateRec = 0

        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()

        execute = 'SELECT hash FROM hashes WHERE dateReceived >= ? ORDER BY dateReceived ASC;'
        args = (dateRec,)
        rows = list()
        for row in c.execute(execute, args):
            for i in row:
                rows.append(i)
        conn.close()
        return rows

    def getBlockDate(self, blockHash):
        '''
            Returns the date a block was received
        '''

        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()

        execute = 'SELECT dateReceived FROM hashes WHERE hash=?;'
        args = (blockHash,)
        for row in c.execute(execute, args):
            for i in row:
                return int(i)
        conn.close()
        return None

    def getBlocksByType(self, blockType, orderDate=True):
        '''
            Returns a list of blocks by the type
        '''

        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()

        if orderDate:
            execute = 'SELECT hash FROM hashes WHERE dataType=? ORDER BY dateReceived;'
        else:
            execute = 'SELECT hash FROM hashes WHERE dataType=?;'

        args = (blockType,)
        rows = list()

        for row in c.execute(execute, args):
            for i in row:
                rows.append(i)
        conn.close()
        return rows

    def getExpiredBlocks(self):
        '''Returns a list of expired blocks'''
        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()
        date = int(self._utils.getEpoch())

        execute = 'SELECT hash FROM hashes WHERE expire <= %s ORDER BY dateReceived;' % (date,)

        rows = list()
        for row in c.execute(execute):
            for i in row:
                rows.append(i)
        conn.close()
        return rows

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

        if key not in ('dateReceived', 'decrypted', 'dataType', 'dataFound', 'dataSaved', 'sig', 'author', 'dateClaimed', 'expire'):
            return False

        conn = sqlite3.connect(self.blockDB, timeout=30)
        c = conn.cursor()
        args = (data, hash)
        c.execute("UPDATE hashes SET " + key + " = ? where hash = ?;", args)
        conn.commit()
        conn.close()

        return True

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

        createTime = self._utils.getRoundedEpoch()

        # check nonce
        #print(data)
        dataNonce = self._utils.bytesToStr(self._crypto.sha3Hash(data))
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
            if self._utils.validatePubKey(asymPeer):
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
                if self._utils.localCommand('/ping', maxWait=10) == 'pong!':
                    self._utils.localCommand('/waitforshare/' + retData, post=True, maxWait=5)
                    self.daemonQueueAdd('uploadBlock', retData)
                self.addToBlockDB(retData, selfInsert=True, dataSaved=True)
                self._utils.processBlockMetadata(retData)

        if retData != False:
            if plaintextPeer == onionrvalues.DENIABLE_PEER_ADDRESS:
                events.event('insertdeniable', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': self._utils.bytesToStr(asymPeer)}, onionr = self.onionrInst, threaded = True)
            else:
                events.event('insertblock', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': self._utils.bytesToStr(asymPeer)}, onionr = self.onionrInst, threaded = True)
        return retData

    def introduceNode(self):
        '''
            Introduces our node into the network by telling X many nodes our HS address
        '''
        if self._utils.localCommand('/ping', maxWait=10) == 'pong!':
            self.daemonQueueAdd('announceNode')
            logger.info('Introduction command will be processed.')
        else:
            logger.warn('No running node detected. Cannot introduce.')