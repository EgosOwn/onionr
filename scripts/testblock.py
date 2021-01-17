#!/usr/bin/env python3

import sys
import os
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
import oldblocks

expire = 600
print(oldblocks.insert(data=os.urandom(32), expire=expire))

