'''
    Onionr - P2P Anonymous Data Storage & Sharing

    DBCreator, creates sqlite3 databases used by Onionr
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
import sqlite3, os
class DBCreator:
    def __init__(self, coreInst):
        self.core = coreInst

    def createAddressDB(self):
        '''
            Generate the address database

            types:
                1: I2P b32 address
                2: Tor v2 (like facebookcorewwwi.onion)
                3: Tor v3
        '''
        conn = sqlite3.connect(self.core.addressDB)
        c = conn.cursor()
        c.execute('''CREATE TABLE adders(
            address text,
            type int,
            knownPeer text,
            speed int,
            success int,
            DBHash text,
            powValue text,
            failure int,
            lastConnect int,
            lastConnectAttempt int,
            trust int
            );
        ''')
        conn.commit()
        conn.close()

    def createPeerDB(self):
        '''
            Generate the peer sqlite3 database and populate it with the peers table.
        '''
        # generate the peer database
        conn = sqlite3.connect(self.core.peerDB)
        c = conn.cursor()
        c.execute('''CREATE TABLE peers(
            ID text not null,
            name text,
            adders text,
            forwardKey text,
            dateSeen not null,
            bytesStored int,
            trust int,
            pubkeyExchanged int,
            hashID text,
            pow text not null);
        ''')
        conn.commit()
        conn.close()
        return

    def createBlockDB(self):
        '''
            Create a database for blocks

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
        if os.path.exists(self.core.blockDB):
            raise Exception("Block database already exists")
        conn = sqlite3.connect(self.core.blockDB)
        c = conn.cursor()
        c.execute('''CREATE TABLE hashes(
            hash text not null,
            dateReceived int,
            decrypted int,
            dataType text,
            dataFound int,
            dataSaved int,
            sig text,
            author text,
            dateClaimed int
            );
        ''')
        conn.commit()
        conn.close()
        return