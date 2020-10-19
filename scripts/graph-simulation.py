from typing import NamedTuple, List

from hashlib import sha3_256
from secrets import randbelow
from random import SystemRandom

WeightedEdge = NamedTuple("WeightedEdge", "node", "weight")

message_pool: Set["Message"] = set()  # This is just to save memory for the simulation

def get_message(hash_id):
    for m in message_pool:
        if hash_id == m.hash_id:
            return m
    raise ValueError

class Node:
    def __init__(self, hidden_node: bool,
                 edges: List[WeightedEdge], graph_ids=["main"]):
        self.hidden_node = hidden_node
        self.edges = edges
        self._messages: List[str] = list()  # hashes point to message_pool
        self._hidden_messages = List[str] = list()

    def sharing_messages(self):
        share = list(self._messages)
        for m in self._hidden_messages:
            share.remove(m)
        return share


    def add_message(self, hash_id):
        if hash_id not in self._messages:
            self._messages.append(message.hash_id)

    def pick_edge(self):
        selected = self.edges[0]
        alt = []

        for weighted_edge in self.edges[1:]:
            if weighted_edge.weight > selected.weight:
                selected = weighted_edge
            elif weighted_edge.weight == selected.weight:
                alt.append(selected)
        alt.append(selected)
        SystemRandom().shuffle(alt)
        return alt[0]


    def share_to_edges(self, message_id):
        edge = self.pick_edge()
        edge.node.add_message(message_id)
        edge.weight += 1

    def lookup_messages(self):
        edge = self.pick_edge()
        for message in edge.node.sharing_messages:
            if message.hash_id not in self._messages:
                self._messages.append(message.hash_id)
        edge.weight += 1

    def make_new_connections(self):
        edge = self.pick_edge()
        for new_edge in edge.edges:
            if new_edge not in self.edges:
                self.edges.append(WeightedEdge(new_edge.node, 0))
        edge.weight += 1


class Message:
    def __init__(self, data):
        def _do_hash(data):
            h = sha3_256()
            h.update(data)
            return h.digest()
        self.hash_id = _do_hash(data)
        self.data = data

bootstrap_node = Node(False, [])
graph = [bootstrap_node]

for i in range(10):
    graph.append(Node(False, [bootstrap_node]))

m = Message("hello world")
message_pool.add(m)
bootstrap_node.add_message(m)
while True:
    for node in graph:
        node.make_new_connections()
        node.lookup_messages()
        bootstrap_node.add_message(m)
