"""Onionr - Private P2P Communication.

DBCreator, creates sqlite3 databases used by Onionr
"""
"""
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
"""
import sqlite3, os
from coredb import dbfiles
import filepaths

def createAddressDB():
    '''
        Generate the address database

        types:
            1: I2P b32 address
            2: Tor v2 (like facebookcorewwwi.onion)
            3: Tor v3
    '''
    if os.path.exists(dbfiles.address_info_db):
        raise FileExistsError("Address database already exists")
    conn = sqlite3.connect(dbfiles.address_info_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE adders(
        address text,
        type int,
        knownPeer text,
        speed int,
        success int,
        powValue text,
        failure int,
        lastConnect int,
        lastConnectAttempt int,
        trust int,
        introduced int
        );
    ''')
    conn.commit()
    conn.close()

def createPeerDB():
    '''
        Generate the peer sqlite3 database and populate it with the peers table.
    '''
    if os.path.exists(dbfiles.user_id_info_db):
        raise FileExistsError("User database already exists")
    # generate the peer database
    conn = sqlite3.connect(dbfiles.user_id_info_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE peers(
        ID text not null,
        name text,
        adders text,
        dateSeen not null,
        trust int,
        hashID text);
    ''')
    c.execute('''CREATE TABLE forwardKeys(
    peerKey text not null,
    forwardKey text not null,
    date int not null,
    expire int not null
    );''')
    conn.commit()
    conn.close()
    return

def createBlockDB():
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
        expire int   - block expire date in epoch
    '''
    if os.path.exists(dbfiles.block_meta_db):
        raise FileExistsError("Block database already exists")
    conn = sqlite3.connect(dbfiles.block_meta_db)
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
        dateClaimed int,
        expire int
        );
    ''')
    conn.commit()
    conn.close()
    return

def createBlockDataDB():
    if os.path.exists(dbfiles.block_data_db):
        raise FileExistsError("Block data database already exists")
    else:
        if not os.path.exists(filepaths.block_data_location):
            os.mkdir(filepaths.block_data_location)
    conn = sqlite3.connect(dbfiles.block_data_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE blockData(
        hash text not null,
        data blob not null
        );
    ''')
    conn.commit()
    conn.close()

def createForwardKeyDB():
    '''
        Create the forward secrecy key db (*for *OUR* keys*)
    '''
    if os.path.exists(dbfiles.forward_keys_db):
        raise FileExistsError("Block database already exists")
    conn = sqlite3.connect(dbfiles.forward_keys_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE myForwardKeys(
        peer text not null,
        publickey text not null,
        privatekey text not null,
        date int not null,
        expire int not null
        );
    ''')
    conn.commit()
    conn.close()
    return


def create_blacklist_db():
    if os.path.exists(dbfiles.blacklist_db):
        raise FileExistsError("Blacklist db already exists")
    conn = sqlite3.connect(dbfiles.blacklist_db, timeout=10)
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE blacklist(
            hash text primary key not null,
            dataType int,
            blacklistDate int,
            expire int
            );
        ''')
    conn.commit()
    conn.close()


create_funcs = [createAddressDB, createPeerDB,
                createBlockDB, createBlockDataDB,
                createForwardKeyDB, create_blacklist_db]