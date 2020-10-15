import sys
import os
import stem

if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
from coredb.blockmetadb import get_block_list

for bl in get_block_list():
    print(bl)
