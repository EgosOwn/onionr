import networkx as nx
import matplotlib.pyplot as plt
import sys
import os
import subprocess
import base64
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
from streamfill import identify_neighbors

G = nx.Graph()
size = 20

onions = []
p = subprocess.Popen(["scripts/generate-onions.py", str(size)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
for line in iter(p.stdout.readline, b''):
    line = line.decode().strip()
    onions.append(line)
    G.add_node(line[:4])

for onion in onions:
    neighbors = identify_neighbors(onion, onions, 0.25 * size)
    for neighbor in neighbors:
        G.add_edge(onion[:4], neighbor[:4])

#nx.draw(G, with_labels=True, font_weight='bold')
#nx.draw_shell(G, with_labels=True)
#nx.draw_random(G, with_labels=True)
nx.draw_kamada_kawai(G, with_labels=True)
plt.savefig("graph.png")