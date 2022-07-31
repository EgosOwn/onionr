from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from onionrblocks import Block

import db

from .dbpath import block_db_path

def delete_block(block: 'Block'):  db.delete(block_db_path, block.id)