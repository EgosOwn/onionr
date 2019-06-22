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