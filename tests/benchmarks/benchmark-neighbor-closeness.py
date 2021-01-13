import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import subprocess
import time

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs, identifyhome
from streamfill import identify_neighbors

onions = []
p = subprocess.Popen(["scripts/generate-onions.py", '50000'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
for line in iter(p.stdout.readline, b''):
    line = line.decode()
    onions.append(line.strip())
p.terminate()

p = subprocess.Popen(["scripts/generate-onions.py", '1'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
for line in iter(p.stdout.readline, b''):
    us = line.decode().strip()
p.terminate()

start = time.time()
identify_neighbors(us, onions, 5)
print(time.time() - start)


