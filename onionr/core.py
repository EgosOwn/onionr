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
import sqlite3, os, sys, time, math, gnupg, base64, tarfile, getpass, simplecrypt, hashlib, nacl
from Crypto.Cipher import AES
from Crypto import Random
import netcontroller

if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        sys.stderr.write('On Python 3 versions prior to 3.6.x, you need the sha3 module')
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

        return

    def generateMainPGP(self, myID):
        ''' Generate the main PGP key for our client. Should not be done often.
        Uses own PGP home folder in the data/ directory. '''
        # Generate main pgp key
        if os.getenv('TRAVIS') == 'true':
            gpg = gnupg.GPG(homedir='./data/pgp/')
        else:
            gpg = gnupg.GPG(gnupghome='./data/pgp/')
        input_data = gpg.gen_key_input(key_type="RSA", key_length=2048, name_real=myID, name_email='anon@onionr')
        #input_data = gpg.gen_key_input(key_type="RSA", key_length=1024)
        key = gpg.gen_key(input_data)
        # Write the key
        myFingerpintFile = open('data/own-fingerprint.txt', 'w')
        myFingerpintFile.write(key.fingerprint)
        myFingerpintFile.close()
        return

    def addPeer(self, peerID, name=''):
        ''' Add a peer by their ID, with an optional name, to the peer database.'''
        ''' DOES NO SAFETY CHECKS if the ID is valid, but prepares the insertion. '''
        # This function simply adds a peer to the DB
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        t = (peerID, name, 'unknown')
        c.execute('Insert into peers (id, name, dateSeen) values(?, ?, ?);', t)
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
            dataFound int
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
        dataFile = open(self.blockDataLocation + hash + '.dat')
        data = dataFile.read()
        dataFile.close()
        return data

    def setData(self, data):
        '''set the data assciated with a hash'''
        hasher = hashlib.sha3_256

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

    def generateHMAC(self):
        '''
        generate and return an HMAC key
        '''
        key = base64.b64encode(os.urandom(32))
        return key