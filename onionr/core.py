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
import sqlite3, os, sys, time, math, base64, tarfile, getpass, simplecrypt, hashlib, nacl, logger, json, netcontroller, math, config
from onionrblockapi import Block

import onionrutils, onionrcrypto, onionrproofs, onionrevents as events, onionrexceptions, onionrvalues
import onionrblacklist
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
            self.queueDB = 'data/queue.db'
            self.peerDB = 'data/peers.db'
            self.blockDB = 'data/blocks.db'
            self.blockDataLocation = 'data/blocks/'
            self.addressDB = 'data/address.db'
            self.hsAddress = ''
            self.bootstrapFileLocation = 'static-data/bootstrap-nodes.txt'
            self.bootstrapList = []
            self.requirements = onionrvalues.OnionrValues()
            self.torPort = torPort
            self.dataNonceFile = 'data/block-nonces.dat'
            self.dbCreate = dbcreator.DBCreator(self)

            self.usageFile = 'data/disk-usage.txt'
            self.config = config

            self.maxBlockSize = 10000000 # max block size in bytes

            if not os.path.exists('data/'):
                os.mkdir('data/')
            if not os.path.exists('data/blocks/'):
                os.mkdir('data/blocks/')
            if not os.path.exists(self.blockDB):
                self.createBlockDB()

            if os.path.exists('data/hs/hostname'):
                with open('data/hs/hostname', 'r') as hs:
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
        '''Hack to refresh some vars which may not be set on first start'''
        if os.path.exists('data/hs/hostname'):
            with open('data/hs/hostname', 'r') as hs:
                self.hsAddress = hs.read().strip()

    def addPeer(self, peerID, powID, name=''):
        '''
            Adds a public key to the key database (misleading function name)
        '''
        # This function simply adds a peer to the DB
        if not self._utils.validatePubKey(peerID):
            return False
        if sys.getsizeof(powID) > 120:
            logger.warn("POW token for pubkey base64 representation exceeded 120 bytes, is " + str(sys.getsizeof(powID)))
            return False

        conn = sqlite3.connect(self.peerDB)
        hashID = self._crypto.pubKeyHashID(peerID)
        c = conn.cursor()
        t = (peerID, name, 'unknown', hashID, powID, 0)

        for i in c.execute("SELECT * FROM PEERS where id = '" + peerID + "';"):
            try:
                if i[0] == peerID:
                    conn.close()
                    return False
            except ValueError:
                pass
            except IndexError:
                pass
        c.execute('INSERT INTO peers (id, name, dateSeen, pow, hashID, trust) VALUES(?, ?, ?, ?, ?, ?);', t)
        conn.commit()
        conn.close()

        return True

    def addAddress(self, address):
        '''
            Add an address to the address database (only tor currently)
        '''
        if address == config.get('i2p.own_addr', None):

            return False
        if self._utils.validateID(address):
            conn = sqlite3.connect(self.addressDB)
            c = conn.cursor()
            # check if address is in database
            # this is safe to do because the address is validated above, but we strip some chars here too just in case
            address = address.replace('\'', '').replace(';', '').replace('"', '').replace('\\', '')
            for i in c.execute("SELECT * FROM adders where address = '" + address + "';"):
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
            logger.debug('Invalid ID')
            return False

    def removeAddress(self, address):
        '''
            Remove an address from the address database
        '''
        if self._utils.validateID(address):
            conn = sqlite3.connect(self.addressDB)
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
            conn = sqlite3.connect(self.blockDB)
            c = conn.cursor()
            t = (block,)
            c.execute('Delete from hashes where hash=?;', t)
            conn.commit()
            conn.close()
            blockFile = 'data/blocks/' + block + '.dat'
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
        conn = sqlite3.connect(self.blockDB)
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

    def _getSha3Hash(self, data):
        hasher = hashlib.sha3_256()
        if not type(data) is bytes:
            data = data.encode()
        hasher.update(data)
        dataHash = hasher.hexdigest()
        return dataHash

    def setData(self, data):
        '''
            Set the data assciated with a hash
        '''
        data = data
        dataSize = sys.getsizeof(data)

        if not type(data) is bytes:
            data = data.encode()

        dataHash = self._getSha3Hash(data)

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
                conn = sqlite3.connect(self.blockDB)
                c = conn.cursor()
                c.execute("UPDATE hashes SET dataSaved=1 WHERE hash = '" + dataHash + "';")
                conn.commit()
                conn.close()
                with open(self.dataNonceFile, 'a') as nonceFile:
                    nonceFile.write(dataHash + '\n')
            else:
                raise onionrexceptions.DiskAllocationReached

        return dataHash

    def dataDirEncrypt(self, password):
        '''
            Encrypt the data directory on Onionr shutdown
        '''
        if os.path.exists('data.tar'):
            os.remove('data.tar')
        tar = tarfile.open("data.tar", "w")
        for name in ['data']:
            tar.add(name)
        tar.close()
        tarData = open('data.tar', 'r',  encoding = "ISO-8859-1").read()
        encrypted = simplecrypt.encrypt(password, tarData)
        open('data-encrypted.dat', 'wb').write(encrypted)
        os.remove('data.tar')

        return

    def dataDirDecrypt(self, password):
        '''
            Decrypt the data directory on startup
        '''
        if not os.path.exists('data-encrypted.dat'):
            return (False, 'encrypted archive does not exist')
        data = open('data-encrypted.dat', 'rb').read()
        try:
            decrypted = simplecrypt.decrypt(password, data)
        except simplecrypt.DecryptionException:
            return (False, 'wrong password (or corrupted archive)')
        else:
            open('data.tar', 'wb').write(decrypted)
            tar = tarfile.open('data.tar')
            tar.extractall()
            tar.close()

        return (True, '')

    def daemonQueue(self):
        '''
            Gives commands to the communication proccess/daemon by reading an sqlite3 database

            This function intended to be used by the client. Queue to exchange data between "client" and server.
        '''
        retData = False
        if not os.path.exists(self.queueDB):
            self.makeDaemonDB()
        else:
            conn = sqlite3.connect(self.queueDB)
            c = conn.cursor()
            try:
                for row in c.execute('SELECT command, data, date, min(ID) FROM commands group by id'):
                    retData = row
                    break
            except sqlite3.OperationalError:
                self.makeDaemonDB()
            else:
                if retData != False:
                    c.execute('DELETE FROM commands WHERE id=?;', (retData[3],))
            conn.commit()
            conn.close()

        events.event('queue_pop', data = {'data': retData}, onionr = None)

        return retData

    def makeDaemonDB(self):
        '''generate the daemon queue db'''
        conn = sqlite3.connect(self.queueDB)
        c = conn.cursor()
        # Create table
        c.execute('''CREATE TABLE commands
                    (id integer primary key autoincrement, command text, data text, date text)''')
        conn.commit()
        conn.close()

    def daemonQueueAdd(self, command, data=''):
        '''
            Add a command to the daemon queue, used by the communication daemon (communicator.py)
        '''
        retData = True
        # Intended to be used by the web server
        date = self._utils.getEpoch()
        conn = sqlite3.connect(self.queueDB)
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
        conn = sqlite3.connect(self.queueDB)
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
        conn = sqlite3.connect(self.addressDB)
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
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        payload = ""
        if trust not in (0, 1, 2):
            logger.error('Tried to select invalid trust.')
            return
        if randomOrder:
            payload = 'SELECT * FROM peers where trust >= %s ORDER BY RANDOM();' % (trust,)
        else:
            payload = 'SELECT * FROM peers where trust >= %s;' % (trust,)
        peerList = []
        for i in c.execute(payload):
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
            forwardKey text,    3
            dateSeen not null,  4
            bytesStored int,    5
            trust int           6
            pubkeyExchanged int 7
            hashID text         8
            pow text            9
        '''
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        command = (peer,)
        infoNumbers = {'id': 0, 'name': 1, 'adders': 2, 'forwardKey': 3, 'dateSeen': 4, 'bytesStored': 5, 'trust': 6, 'pubkeyExchanged': 7, 'hashID': 8}
        info = infoNumbers[info]
        iterCount = 0
        retVal = ''
        for row in c.execute('SELECT * from peers where id=?;', command):
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
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        command = (data, peer)
        # TODO: validate key on whitelist
        if key not in ('id', 'name', 'pubkey', 'blockDBHash', 'forwardKey', 'dateSeen', 'bytesStored', 'trust'):
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
            failure int 6
            lastConnect 7
        '''
        conn = sqlite3.connect(self.addressDB)
        c = conn.cursor()
        command = (address,)
        infoNumbers = {'address': 0, 'type': 1, 'knownPeer': 2, 'speed': 3, 'success': 4, 'DBHash': 5, 'failure': 6, 'lastConnect': 7}
        info = infoNumbers[info]
        iterCount = 0
        retVal = ''
        for row in c.execute('SELECT * from adders where address=?;', command):
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
        conn = sqlite3.connect(self.addressDB)
        c = conn.cursor()
        command = (data, address)
        # TODO: validate key on whitelist
        if key not in ('address', 'type', 'knownPeer', 'speed', 'success', 'DBHash', 'failure', 'lastConnect', 'lastConnectAttempt'):
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
        conn = sqlite3.connect(self.blockDB)
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
        conn = sqlite3.connect(self.blockDB)
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
        conn = sqlite3.connect(self.blockDB)
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

    def setBlockType(self, hash, blockType):
        '''
            Sets the type of block
        '''

        conn = sqlite3.connect(self.blockDB)
        c = conn.cursor()
        c.execute("UPDATE hashes SET dataType='" + blockType + "' WHERE hash = '" + hash + "';")
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
        '''

        if key not in ('dateReceived', 'decrypted', 'dataType', 'dataFound', 'dataSaved', 'sig', 'author', 'dateClaimed'):
            return False

        conn = sqlite3.connect(self.blockDB)
        c = conn.cursor()
        args = (data, hash)
        c.execute("UPDATE hashes SET " + key + " = ? where hash = ?;", args)
        conn.commit()
        conn.close()
        return True

    def insertBlock(self, data, header='txt', sign=False, encryptType='', symKey='', asymPeer='', meta = dict()):
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
        if not header is None:
            meta['type'] = header
        meta['type'] = str(meta['type'])

        jsonMeta = json.dumps(meta)

        if encryptType in ('asym', 'sym', ''):
            metadata['encryptType'] = encryptType
        else:
            raise onionrexceptions.InvalidMetadata('encryptType must be asym or sym, or blank')

        try:
            data = data.encode()
        except AttributeError:
            pass
        # sign before encrypt, as unauthenticated crypto should not be a problem here
        if sign:
            signature = self._crypto.edSign(jsonMeta.encode() + data, key=self._crypto.privKey, encodeResult=True)
            signer = self._crypto.pubKey

        if len(jsonMeta) > 1000:
            raise onionrexceptions.InvalidMetadata('meta in json encoded form must not exceed 1000 bytes')

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
                jsonMeta = self._crypto.pubKeyEncrypt(jsonMeta, asymPeer, encodedData=True, anonymous=True).decode()
                data = self._crypto.pubKeyEncrypt(data, asymPeer, encodedData=True, anonymous=True).decode()
                signature = self._crypto.pubKeyEncrypt(signature, asymPeer, encodedData=True, anonymous=True).decode()
                signer = self._crypto.pubKeyEncrypt(signer, asymPeer, encodedData=True, anonymous=True).decode()
            else:
                raise onionrexceptions.InvalidPubkey(asymPeer + ' is not a valid base32 encoded ed25519 key')

        # compile metadata
        metadata['meta'] = jsonMeta
        metadata['sig'] = signature
        metadata['signer'] = signer
        metadata['time'] = str(self._utils.getEpoch())

        # send block data (and metadata) to POW module to get tokenized block data
        proof = onionrproofs.POW(metadata, data)
        payload = proof.waitForResult()
        if payload != False:
            retData = self.setData(payload)
            self.addToBlockDB(retData, selfInsert=True, dataSaved=True)
            self.setBlockType(retData, meta['type'])
            self.daemonQueueAdd('uploadBlock', retData)

        if retData != False:
            events.event('insertBlock', onionr = None, threaded = False)
        return retData

    def introduceNode(self):
        '''
            Introduces our node into the network by telling X many nodes our HS address
        '''

        if(self._utils.isCommunicatorRunning()):
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
