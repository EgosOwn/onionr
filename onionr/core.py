'''
    Onionr - P2P Microblogging Platform & Social network

    Core Onionr library, useful for external programs. Handles peer processing and cryptography.
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
import sqlite3, os, sys, time, math, gnupg, base64, tarfile, getpass, simplecrypt, hashlib, nacl, logger
from Crypto.Cipher import AES
from Crypto import Random
import netcontroller

import onionrutils

if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        logger.fatal('On Python 3 versions prior to 3.6.x, you need the sha3 module')
        sys.exit(1)

class Core:
    def __init__(self):
        '''
        Initialize Core Onionr library
        '''
        self.queueDB = 'data/queue.db'
        self.peerDB = 'data/peers.db'
        self.ownPGPID = ''
        self.blockDB = 'data/blocks.db'
        self.blockDataLocation = 'data/blocks/'
        self._utils = onionrutils.OnionrUtils(self)

        if not os.path.exists('data/'):
            os.mkdir('data/')
        if not os.path.exists('data/blocks/'):
            os.mkdir('data/blocks/')

        if not os.path.exists(self.blockDB):
            self.createBlockDB()

        return

    def generateMainPGP(self, myID):
        ''' Generate the main PGP key for our client. Should not be done often.
        Uses own PGP home folder in the data/ directory. '''
        # Generate main pgp key
        gpg = gnupg.GPG(homedir='./data/pgp/')
        input_data = gpg.gen_key_input(key_type="RSA", key_length=1024, name_real=myID, name_email='anon@onionr', testing=True)
        #input_data = gpg.gen_key_input(key_type="RSA", key_length=1024)
        key = gpg.gen_key(input_data)
        logger.info("Generating PGP key, this will take some time..")
        while key.status != "key created":
            time.sleep(0.5)
            print(key.status)
        logger.info("Finished generating PGP key")
        # Write the key
        myFingerpintFile = open('data/own-fingerprint.txt', 'w')
        myFingerpintFile.write(key.fingerprint)
        myFingerpintFile.close()
        return

    def addPeer(self, peerID, name=''):
        ''' Add a peer by their ID, with an optional name, to the peer database.'''
        ''' DOES NO SAFETY CHECKS if the ID is valid, but prepares the insertion. '''
        # This function simply adds a peer to the DB
        if not self._utils.validateID(peerID):
            return False
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        t = (peerID, name, 'unknown')
        c.execute('insert into peers (id, name, dateSeen) values(?, ?, ?);', t)
        conn.commit()
        conn.close()
        return True

    def createPeerDB(self):
        '''
        Generate the peer sqlite3 database and populate it with the peers table.
        '''
        # generate the peer database
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        c.execute('''
        create table peers(
        ID text not null,
        name text,
        pgpKey text,
        hmacKey text,
        blockDBHash text,
        forwardKey text,
        dateSeen not null,
        bytesStored int,
        trust int);
        ''')
        conn.commit()
        conn.close()
    def createBlockDB(self):
        '''
        Create a database for blocks

        hash - the hash of a block
        dateReceived - the date the block was recieved, not necessarily when it was created
        decrypted - if we can successfully decrypt the block (does not describe its current state)
        dataObtained - if the data has been obtained for the block
        '''
        if os.path.exists(self.blockDB):
            raise Exception("Block database already exists")
        conn = sqlite3.connect(self.blockDB)
        c = conn.cursor()
        c.execute('''create table hashes(
            hash text not null,
            dateReceived int,
            decrypted int,
            dataFound int,
            dataSaved int
        );
        ''')
        conn.commit()
        conn.close()
    def addToBlockDB(self, newHash):
        '''add a hash value to the block db (should be in hex format)'''
        if not os.path.exists(self.blockDB):
            raise Exception('Block db does not exist')
        conn = sqlite3.connect(self.blockDB)
        c = conn.cursor()
        currentTime = math.floor(time.time())
        data = (newHash, currentTime, 0, 0)
        c.execute('INSERT into hashes values(?, ?, ?, ?);', data)
        conn.commit()
        conn.close()

    def getData(self,hash):
        '''simply return the data associated to a hash'''
        try:
            dataFile = open(self.blockDataLocation + hash + '.dat')
            data = dataFile.read()
            dataFile.close()
        except FileNotFoundError:
            data = False
        return data

    def setData(self, data):
        '''set the data assciated with a hash'''
        data = data.encode()
        hasher = hashlib.sha3_256()
        hasher.update(data)
        dataHash = hasher.hexdigest()
        blockFileName = self.blockDataLocation + dataHash + '.dat'
        if os.path.exists(blockFileName):
            raise Exception("Data is already set for " + dataHash)
        else:
            blockFile = open(blockFileName, 'w')
            blockFile.write(data.decode())
            blockFile.close()
        return dataHash

    def dataDirEncrypt(self, password):
        '''
        Encrypt the data directory on Onionr shutdown
        '''
        # Encrypt data directory (don't delete it in this function)
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
        # Decrypt data directory
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
        '''
        # This function intended to be used by the client
        # Queue to exchange data between "client" and server.
        retData = False
        if not os.path.exists(self.queueDB):
            conn = sqlite3.connect(self.queueDB)
            c = conn.cursor()
            # Create table
            c.execute('''CREATE TABLE commands
                        (id integer primary key autoincrement, command text, data text, date text)''')
            conn.commit()
        else:
            conn = sqlite3.connect(self.queueDB)
            c = conn.cursor()
            for row in c.execute('SELECT command, data, date, min(ID) FROM commands group by id'):
                retData = row
                break
            if retData != False:
                c.execute('delete from commands where id = ?', (retData[3],))
        conn.commit()
        conn.close()

        return retData

    def daemonQueueAdd(self, command, data=''):
        '''
        Add a command to the daemon queue, used by the communication daemon (communicator.py)
        '''
        # Intended to be used by the web server
        date = math.floor(time.time())
        conn = sqlite3.connect(self.queueDB)
        c = conn.cursor()
        t = (command, data, date)
        c.execute('INSERT into commands (command, data, date) values (?, ?, ?)', t)
        conn.commit()
        conn.close()
        return
    def clearDaemonQueue(self):
        '''clear the daemon queue (somewhat dangerousous)'''
        conn = sqlite3.connect(self.queueDB)
        c = conn.cursor()
        try:
            c.execute('delete from commands;')
            conn.commit()
        except:
            pass
        conn.close()

    def generateHMAC(self):
        '''
        generate and return an HMAC key
        '''
        key = base64.b64encode(os.urandom(32))
        return key

    def listPeers(self, randomOrder=True):
        '''Return a list of peers

        randomOrder determines if the list should be in a random order
        '''
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        if randomOrder:
            peers = c.execute('SELECT * FROM peers order by RANDOM();')
        else:
            peers = c.execute('SELECT * FROM peers;')
        peerList = []
        for i in peers:
            peerList.append(i[0])
        conn.close()
        return peerList

    def processBlocks(self):
        '''
        Work with the block database and download any missing blocks
        This is meant to be called from the communicator daemon on its timer.
        '''
        for i in self.getBlockList(True):
            print('UNSAVED BLOCK:', i)
        return
    def getPeerInfo(self, peer, info):
        '''
        get info about a peer

        id text             0
        name text,          1
        pgpKey text,        2
        hmacKey text,       3
        blockDBHash text,   4
        forwardKey text,    5
        dateSeen not null,  7
        bytesStored int,    8
        trust int           9
        '''
        # Lookup something about a peer from their database entry
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        command = (peer,)
        infoNumbers = {'id': 0, 'name': 1, 'pgpKey': 2, 'hmacKey': 3, 'blockDBHash': 4, 'forwardKey': 5, 'dateSeen': 6, 'bytesStored': 7, 'trust': 8}
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
        '''update a peer for a key'''
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        command = (data, peer)
        # TODO: validate key on whitelist

        c.execute('UPDATE peers SET ' + key + ' = ? where id=?', command)
        conn.commit()
        conn.close()

    def getBlockList(self, unsaved=False):
        '''get list of our blocks'''
        conn = sqlite3.connect(self.blockDB)
        c = conn.cursor()
        retData = ''
        if unsaved:
            execute = 'SELECT hash FROM hashes where dataSaved != 1;'
        else:
            execute = 'SELECT hash FROM hashes;'
        for row in c.execute(execute):
            for i in row:
                retData += i
        return retData
