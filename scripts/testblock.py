#!/usr/bin/env python3

import sys
import os
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
import onionrblocks

expire = 600
print(onionrblocks.insert(data=os.urandom(32), expire=expire))

