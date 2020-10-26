import sys
import os
import subprocess
import base64
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
from streamfill import identify_neighbors

onions = []
p = subprocess.Popen(["scripts/generate-onions.py", '5'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
for line in iter(p.stdout.readline, b''):
    line = line.decode()
    onions.append(line.strip())


for onion in onions:
    print(onion, identify_neighbors(onion, onions, 3))

