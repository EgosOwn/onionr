'''
    Onionr - Private P2P Communication

    Add an entry to the block metadata database
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
import os, sqlite3
from onionrutils import epoch, blockmetadata
def add_to_block_DB(core_inst, newHash, selfInsert=False, dataSaved=False):
    '''
        Add a hash value to the block db

        Should be in hex format!
    '''

    if not os.path.exists(core_inst.blockDB):
        raise Exception('Block db does not exist')
    if blockmetadata.has_block(core_inst, newHash):
        return
    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()
    currentTime = epoch.get_epoch() + core_inst._crypto.secrets.randbelow(301)
    if selfInsert or dataSaved:
        selfInsert = 1
    else:
        selfInsert = 0
    data = (newHash, currentTime, '', selfInsert)
    c.execute('INSERT INTO hashes (hash, dateReceived, dataType, dataSaved) VALUES(?, ?, ?, ?);', data)
    conn.commit()
    conn.close()