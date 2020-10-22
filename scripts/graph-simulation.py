from typing import NamedTuple, List, Set

from collections import namedtuple
from hashlib import sha3_256
from secrets import randbelow
from random import SystemRandom
from threading import Thread
from time import sleep
import uuid

WeightedEdge = namedtuple("WeightedEdge", ["node", "weight"])

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
        self.node_id = str(uuid.uuid4())
        self._messages: List[str] = list()  # hashes point to message_pool
        self._hidden_messages: List[str] = list()

    def sharing_messages(self):
        share = list(self._messages)
        for m in self._hidden_messages:
            share.remove(m)
        return share


    def add_message(self, hash_id):
        if hash_id not in self._messages:
            self._messages.append(hash_id)

    def pick_edge(self):
        selected = self.edges[0]
        alt = []

        for weighted_edge in self.edges[1:]:
            if weighted_edge.weight[0] > selected.weight:
                selected = weighted_edge
            elif weighted_edge.weight[0] == selected.weight:
                alt.append(selected)
        alt.append(selected)
        SystemRandom().shuffle(alt)
        return alt[0]


    def share_to_edges(self, message_id):
        edge = self.pick_edge()
        edge.node.add_message(message_id)
        edge.weight[0] += 1

    def lookup_messages(self):
        edge = self.pick_edge()
        for message in edge.node.sharing_messages():
            if message.hash_id not in self._messages:
                self._messages.append(message.hash_id)
                print(self.node_id, "found", message.hash_id)
        edge.weight[0] += 1

    def make_new_connections(self):
        edge = self.pick_edge()
        for new_edge in edge.node.edges:
            if new_edge not in self.edges:
                self.edges.append(WeightedEdge(new_edge.node, [0]))
                print(self.node_id, "added peer", new_edge.node.node_id)
        edge.weight[0] += 1


class Message:
    def __init__(self, data):
        def _do_hash(data):
            h = sha3_256()
            h.update(data)
            return h.digest()
        self.hash_id = _do_hash(data)
        self.data = data

bootstrap_node = Node(False, [])
graph = [WeightedEdge(bootstrap_node, [0])]

for i in range(10):
    graph.append(WeightedEdge(Node(False, [WeightedEdge(bootstrap_node, [0])]), [0]))

m = Message(b"hello world")
message_pool.add(m)
bootstrap_node.add_message(m.hash_id)

def node_driver(node):
    while True:
        node.make_new_connections()
        node.lookup_messages()
        sleep(1)

for edge in graph:
    Thread(target=node_driver, args=[edge.node], daemon=True).start()
input()

