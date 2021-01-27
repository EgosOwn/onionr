import blockio


def list_blocks_by_type(safe_db, block_type) -> bytes:
    try:
        return safe_db.get(b'bl-' + block_type)
    except KeyError:
        return b""

def handle_check_block(safe_db, block_hash):
    if block_hash in blockio.list_all_blocks(safe_db):
        return int(1).to_bytes(1, 'little')
    else:
        return int(2).to_bytes(1, 'little')
