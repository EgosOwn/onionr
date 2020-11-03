import sys
import os
import stem

if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
from coredb.blockmetadb import get_block_list
from onionrblocks.onionrblockapi import Block

for bl in get_block_list():
    bl_obj = Block(bl, decrypt=False)
    b_type = bl_obj.getType()
    if not b_type:
        b_type = "encrypted"
    print(bl + " - " + str(bl_obj.date) + " - " + b_type)
