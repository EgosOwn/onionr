import networkx as nx
import matplotlib.pyplot as plt
import networkx.drawing

import json
from hashlib import sha3_256

def do_hash(data):
	h = sha3_256()
	h.update(data.encode())
	return h.digest()


with open('stats.json', 'r') as raw_data:
	raw_data = raw_data.read()

G = nx.MultiGraph()
js = json.loads(raw_data)

for node in js:
	G.add_node(node[:5] + '.onion')

for node in js:
	data = json.loads(js[node])
	for conn_node in data['peers']:
		G.add_edge(node[:5] + '.onion', conn_node[:5] + '.onion')


nx.draw_spring(G, font_weight='bold', with_labels=True)
plt.show()
