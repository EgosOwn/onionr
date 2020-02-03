#!/usr/bin/env python3

"""Spam a bunch of Onionr blocks"""

# Please don't run this script on the real Onionr network. You wouldn't do anything but be annoying

print("Please don't run this script on the real Onionr network. You wouldn't do anything but be annoying, and possibly violate law")

import sys
import os
os.chdir('../')
sys.path.append("src/")
import onionrblocks


amount = int(input("Number of blocks:"))

for i in range(amount):
    onionrblocks.insert(data=os.urandom(32))
    print(i, "done")

