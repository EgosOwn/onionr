'''
    Onionr - Private P2P Communication

    Update block information in the metadata database by a field name
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

import sqlite3
def update_block_info(core_inst, hash, key, data):
    if key not in ('dateReceived', 'decrypted', 'dataType', 'dataFound', 'dataSaved', 'sig', 'author', 'dateClaimed', 'expire'):
        return False

    conn = sqlite3.connect(core_inst.blockDB, timeout=30)
    c = conn.cursor()
    args = (data, hash)
    c.execute("UPDATE hashes SET " + key + " = ? where hash = ?;", args)
    conn.commit()
    conn.close()

    return True