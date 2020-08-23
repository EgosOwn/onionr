#!/usr/bin/env python3

"""Spam a bunch of Onionr blocks"""

# Please don't run this script on the real Onionr network. You wouldn't do anything but be annoying

print("Please don't run this script on Onionr networks that include more than you. You wouldn't do anything but be annoying, and probably violate law")

import sys
import os
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
import onionrblocks


amount = int(input("Number of blocks:"))
expire = input("Expire in seconds:")

if not expire:
    expire = ""
else:
    expire = int(expire)

for i in range(amount):
    if expire:
        print(onionrblocks.insert(data=os.urandom(32), expire=expire))
    else:
        print(onionrblocks.insert(data=os.urandom(32)))
    print(i, "done")

