'''
    Onionr - P2P Microblogging Platform & Social network
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
import sqlite3, os, time, math, gnupg, base64, tarfile, getpass, simplecrypt
from Crypto.Cipher import AES
from Crypto import Random


class Core:
    def __init__(self):
        self.queueDB = 'data/queue.db'
        self.peerDB = 'data/peers.db'

        #self.daemonQueue() # Call to create the DB if it doesn't exist
        return

    def generateMainPGP(self):
        # Generate main pgp key
        gpg = gnupg.GPG(gnupghome='data/pgp/')
        input_data = gpg.gen_key_input(key_type="RSA", key_length=2048, name_real='anon', name_comment='Onionr key', name_email='anon@onionr')
        key = gpg.gen_key(input_data)
        return

    def addPeer(self, id, name=''):
        # This function simply adds a peer to the DB
        return

    def createPeerDB(self):
        # generate the peer database
        conn = sqlite3.connect(self.peerDB)
        c = conn.cursor()
        c.execute('''
        create table users(
        ID text not null,
        name text,
        pgpKey text,
        hmacKey text,
        forwardKey text,
        dateSeen not null,
        trust int);
        ''')
        conn.commit()
        conn.close()
    
    def dataDirEncrypt(self, password):
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
        # Intended to be used by the web server
        date = math.floor(time.time())
        conn = sqlite3.connect(self.queueDB)
        c = conn.cursor()
        t = (command, data, date)
        c.execute('INSERT into commands (command, data, date) values (?, ?, ?)', t)
        conn.commit()
        conn.close()
        return