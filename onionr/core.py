'''
    Onionr - P2P Anonymous Storage Network

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
import sqlite3, os, sys, time, math, base64, tarfile, nacl, logger, json, netcontroller, math, config
from onionrblockapi import Block

import onionrutils, onionrcrypto, onionrproofs, onionrevents as events, onionrexceptions, onionrvalues
import onionrblacklist, onionrchat, onionrusers
import dbcreator

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

        try:
            self.dataDir = os.environ['ONIONR_HOME']
            if not self.dataDir.endswith('/'):
                self.dataDir += '/'
        except KeyError:
            self.dataDir = 'data/'

        try:
            self.queueDB = self.dataDir + 'queue.db'
            self.peerDB = self.dataDir + 'peers.db'
            self.blockDB = self.dataDir + 'blocks.db'
            self.blockDataLocation = self.dataDir + 'blocks/'
            self.publicApiHostFile = self.dataDir + 'public-host.txt'
            self.privateApiHostFile = self.dataDir + 'private-host.txt'
            self.addressDB = self.dataDir + 'address.db'
            self.hsAddress = ''
            self.i2pAddress = config.get('i2p.ownAddr', None)
            self.bootstrapFileLocation = 'static-data/bootstrap-nodes.txt'
            self.bootstrapList = []
            self.requirements = onionrvalues.OnionrValues()
            self.torPort = torPort
            self.dataNonceFile = self.dataDir + 'block-nonces.dat'
            self.dbCreate = dbcreator.DBCreator(self)
            self.forwardKeysFile = self.dataDir + 'forward-keys.db'

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

            self._utils = onionrutils.OnionrUtils(self)
            # Initialize the crypto object
            self._crypto = onionrcrypto.OnionrCrypto(self)
            self._blacklist = onionrblacklist.OnionrBlackList(self)

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

        # This function simply adds a peer to the DB
        if not self._utils.validatePubKey(peerID):
            return False

        events.event('pubkey_add', data = {'key': peerID}, onionr = None)

        conn = sqlite3.connect(self.peerDB, timeout=10)
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

        if address == config.get('i2p.ownAddr', None) or address == self.hsAddress:
            return False
        if type(address) is type(None) or len(address) == 0:
            return False
        if self._utils.validateID(address):
            conn = sqlite3.connect(self.addressDB, timeout=10)
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

            events.event('address_add', data = {'address': address}, onionr = None)

            return True
        else:
            logger.debug('Invalid ID: %s' % address)
            return False

    def removeAddress(self, address):
        '''
            Remove an address from the address database
        '''

        if self._utils.validateID(address):
            conn = sqlite3.connect(self.addressDB, timeout=10)
            c = conn.cursor()
            t = (address,)
            c.execute('Delete from adders where address=?;', t)
            conn.commit()
            conn.close()

            events.event('address_remove', data = {'address': address}, onionr = None)
            return True
        else:
            return False

    def removeBlock(self, block):
        '''
            remove a block from this node (does not automatically blacklist)

            **You may want blacklist.addToDB(blockHash)
        '''

        if self._utils.validateHash(block):
            conn = sqlite3.connect(self.blockDB, timeout=10)
            c = conn.cursor()
            t = (block,)
            c.execute('Delete from hashes where hash=?;', t)
            conn.commit()
            conn.close()
            blockFile = self.dataDir + '/blocks/%s.dat' % block
            dataSize = 0
            try:
                ''' Get size of data when loaded as an object/var, rather than on disk,
                    to avoid conflict with getsizeof when saving blocks
                '''
                with open(blockFile, 'r') as data:
                    dataSize = sys.getsizeof(data.read())
                self._utils.storageCounter.removeBytes(dataSize)
                os.remove(blockFile)
            except FileNotFoundError:
                pass

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
        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()
        currentTime = self._utils.getEpoch()
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

        try:
            # logger.debug('Opening %s' % (str(self.blockDataLocation) + str(hash) + '.dat'))
            dataFile = open(self.blockDataLocation + hash + '.dat', 'rb')
            data = dataFile.read()
            dataFile.close()
        except FileNotFoundError:
            data = False

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
                blockFile = open(blockFileName, 'wb')
                blockFile.write(data)
                blockFile.close()
                conn = sqlite3.connect(self.blockDB, timeout=10)
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
            conn = sqlite3.connect(self.queueDB, timeout=10)
            c = conn.cursor()
            try:
                for row in c.execute('SELECT command, data, date, min(ID) FROM commands group by id'):
                    retData = row
                    break
            except sqlite3.OperationalError:
                self.dbCreate.createDaemonDB()
            else:
                if retData != False:
                    c.execute('DELETE FROM commands WHERE id=?;', (retData[3],))
            conn.commit()
            conn.close()

        events.event('queue_pop', data = {'data': retData}, onionr = None)

        return retData

    def daemonQueueAdd(self, command, data=''):
        '''
            Add a command to the daemon queue, used by the communication daemon (communicator.py)
        '''

        retData = True
        # Intended to be used by the web server

        date = self._utils.getEpoch()
        conn = sqlite3.connect(self.queueDB, timeout=10)
        c = conn.cursor()
        t = (command, data, date)

        try:
            c.execute('INSERT INTO commands (command, data, date) VALUES(?, ?, ?)', t)
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            retData = False
            self.daemonQueue()
        events.event('queue_push', data = {'command': command, 'data': data}, onionr = None)
        return retData

    def clearDaemonQueue(self):
        '''
            Clear the daemon queue (somewhat dangerous)
        '''
        conn = sqlite3.connect(self.queueDB, timeout=10)
        c = conn.cursor()

        try:
            c.execute('DELETE FROM commands;')
            conn.commit()
        except:
            pass

        conn.close()
        events.event('queue_clear', onionr = None)

        return

    def listAdders(self, randomOrder=True, i2p=True):
        '''
            Return a list of addresses
        '''
        conn = sqlite3.connect(self.addressDB, timeout=10)
        c = conn.cursor()
        if randomOrder:
            addresses = c.execute('SELECT * FROM adders ORDER BY RANDOM();')
        else:
            addresses = c.execute('SELECT * FROM adders;')
        addressList = []
        for i in addresses:
            addressList.append(i[0])
        conn.close()
        return addressList

    def listPeers(self, randomOrder=True, getPow=False, trust=0):
        '''
            Return a list of public keys (misleading function name)

            randomOrder determines if the list should be in a random order
            trust sets the minimum trust to list
        '''
        conn = sqlite3.connect(self.peerDB, timeout=10)
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

        if getPow:
            try:
                peerList.append(self._crypto.pubKey + '-' + self._crypto.pubKeyPowToken)
            except TypeError:
                pass
        else:
            peerList.append(self._crypto.pubKey)

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
        conn = sqlite3.connect(self.peerDB, timeout=10)
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

        conn = sqlite3.connect(self.peerDB, timeout=10)
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
            DBHash text, 5
            powValue    6
            failure int 7
            lastConnect 8
            trust       9
            introduced  10
        '''

        conn = sqlite3.connect(self.addressDB, timeout=10)
        c = conn.cursor()

        command = (address,)
        infoNumbers = {'address': 0, 'type': 1, 'knownPeer': 2, 'speed': 3, 'success': 4, 'DBHash': 5, 'powValue': 6, 'failure': 7, 'lastConnect': 8, 'trust': 9, 'introduced': 10}
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

        conn = sqlite3.connect(self.addressDB, timeout=10)
        c = conn.cursor()

        command = (data, address)
        
        if key not in ('address', 'type', 'knownPeer', 'speed', 'success', 'DBHash', 'failure', 'powValue', 'lastConnect', 'lastConnectAttempt', 'trust', 'introduced'):
            raise Exception("Got invalid database key when setting address info")
        else:
            c.execute('UPDATE adders SET ' + key + ' = ? WHERE address=?', command)
            conn.commit()
            conn.close()

        return

    def getBlockList(self, unsaved = False): # TODO: Use unsaved??
        '''
            Get list of our blocks
        '''

        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()

        if unsaved:
            execute = 'SELECT hash FROM hashes WHERE dataSaved != 1 ORDER BY RANDOM();'
        else:
            execute = 'SELECT hash FROM hashes ORDER BY dateReceived ASC;'

        rows = list()
        for row in c.execute(execute):
            for i in row:
                rows.append(i)

        return rows

    def getBlockDate(self, blockHash):
        '''
            Returns the date a block was received
        '''

        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()

        execute = 'SELECT dateReceived FROM hashes WHERE hash=?;'
        args = (blockHash,)
        for row in c.execute(execute, args):
            for i in row:
                return int(i)

        return None

    def getBlocksByType(self, blockType, orderDate=True):
        '''
            Returns a list of blocks by the type
        '''

        conn = sqlite3.connect(self.blockDB, timeout=10)
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

        return rows

    def getExpiredBlocks(self):
        '''Returns a list of expired blocks'''
        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()
        date = int(self._utils.getEpoch())

        execute = 'SELECT hash FROM hashes WHERE expire <= %s ORDER BY dateReceived;' % (date,)

        rows = list()
        for row in c.execute(execute):
            for i in row:
                rows.append(i)
        return rows

    def setBlockType(self, hash, blockType):
        '''
            Sets the type of block
        '''

        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()
        c.execute("UPDATE hashes SET dataType = ? WHERE hash = ?;", (blockType, hash))
        conn.commit()
        conn.close()

        return

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

        conn = sqlite3.connect(self.blockDB, timeout=10)
        c = conn.cursor()
        args = (data, hash)
        c.execute("UPDATE hashes SET " + key + " = ? where hash = ?;", args)
        conn.commit()
        conn.close()

        return True

    def insertBlock(self, data, header='txt', sign=False, encryptType='', symKey='', asymPeer='', meta = {}, expire=None):
        '''
            Inserts a block into the network
            encryptType must be specified to encrypt a block
        '''

        retData = False
        # check nonce
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
            try:
                forwardEncrypted = onionrusers.OnionrUser(self, asymPeer).forwardEncrypt(data)
                data = forwardEncrypted[0]
                meta['forwardEnc'] = True
            except onionrexceptions.InvalidPubkey:
                onionrusers.OnionrUser(self, asymPeer).generateForwardKey()
            onionrusers.OnionrUser(self, asymPeer).generateForwardKey()
            fsKey = onionrusers.OnionrUser(self, asymPeer).getGeneratedForwardKeys()[0]
            meta['newFSKey'] = fsKey[0]
        jsonMeta = json.dumps(meta)
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
                jsonMeta = self._crypto.pubKeyEncrypt(jsonMeta, asymPeer, encodedData=True, anonymous=True).decode()
                data = self._crypto.pubKeyEncrypt(data, asymPeer, encodedData=True, anonymous=True).decode()
                signature = self._crypto.pubKeyEncrypt(signature, asymPeer, encodedData=True, anonymous=True).decode()
                signer = self._crypto.pubKeyEncrypt(signer, asymPeer, encodedData=True, anonymous=True).decode()
                onionrusers.OnionrUser(self, asymPeer, saveUser=True)
            else:
                raise onionrexceptions.InvalidPubkey(asymPeer + ' is not a valid base32 encoded ed25519 key')

        # compile metadata
        metadata['meta'] = jsonMeta
        metadata['sig'] = signature
        metadata['signer'] = signer
        metadata['time'] = self._utils.getRoundedEpoch() + self._crypto.secrets.randbelow(301)

        # ensure expire is integer and of sane length
        if type(expire) is not type(None):
            assert len(str(int(expire))) < 14
            metadata['expire'] = expire

        # send block data (and metadata) to POW module to get tokenized block data
        proof = onionrproofs.POW(metadata, data)
        payload = proof.waitForResult()
        if payload != False:
            retData = self.setData(payload)
            # Tell the api server through localCommand to wait for the daemon to upload this block to make stastical analysis more difficult
            self._utils.localCommand('waitforshare/' + retData)
            self.addToBlockDB(retData, selfInsert=True, dataSaved=True)
            #self.setBlockType(retData, meta['type'])
            self._utils.processBlockMetadata(retData)
            self.daemonQueueAdd('uploadBlock', retData)

        if retData != False:
            events.event('insertBlock', onionr = None, threaded = False)
        return retData

    def introduceNode(self):
        '''
            Introduces our node into the network by telling X many nodes our HS address
        '''

        if(self._utils.isCommunicatorRunning(timeout=30)):
            announceAmount = 2
            nodeList = self.listAdders()

            if len(nodeList) == 0:
                for i in self.bootstrapList:
                    if self._utils.validateID(i):
                        self.addAddress(i)
                        nodeList.append(i)

            if announceAmount > len(nodeList):
                announceAmount = len(nodeList)

            for i in range(announceAmount):
                self.daemonQueueAdd('announceNode', nodeList[i])

            events.event('introduction', onionr = None)

            return True
        else:
            logger.error('Onionr daemon is not running.')
            return False

        return
