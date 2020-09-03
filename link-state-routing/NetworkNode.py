from Node import Node
from Graph import Graph

import eventlet
import socketio
import sys
import uuid

class Network:

    def __init__(self):
        self.node = None
        self.nodes = {}
        self.graph = None
        self.paths = None
        self.id = None
        self.connections = []
    
    def __graph_update(self):
        self.graph = Graph.create_from_nodes([self.nodes[x] for x in self.nodes.keys()])
        self.__update_cons()
    
    def __update_cons(self):
        for conn in self.connections:
            self.graph.connect(self.nodes[conn['from']], self.nodes[conn['to']], int(conn['w']))

    def start(self, id):
        self.id = id
        self.node = Node(id)
        self.nodes[id] = self.node
        self.__graph_update()
    
    def add_new_node(self, node):
        self.nodes[node.data] = node
        self.__graph_update()
    
    def connect_to_node(self, f, t, w):
        self.connections.append({'from': f, 'to': t, 'w': w})
        self.__graph_update()
        self.graph.dijkstra(self.node)
    
    def get_n_ids(self):
        n = []
        for conn in self.connections:
            if conn['from'] == self.id and self.id != conn['to']:
                n.append(n['to'])
        return n

socket = socketio.Client()
nw = Network()

def send_new_node():
    global socket, nw
    socket.emit('new_node', {'id': nw.id, 'pid': str(uuid.uuid1())})

def connect_to_node(id, w):
    global socket, nw
    nw.add_new_node(Node(id))
    nw.connect_to_node(nw.id, id, w)
    socket.emit('connect_to', {'from': nw.id, 'to': id, 'w': w, 'pid': str(uuid.uuid1())})

@socket.on('new_graph_connection')
def on_new_connection(data):
    global socket, nw
    nw.add_new_node(Node(data['from']))
    nw.add_new_node(Node(data['to']))
    nw.connect_to_node(data['from'], data['to'], int(data['w']))
    nids = nw.get_n_ids()
    for n in nids:
        socket.emit('send_to', {'to': n, 'data': data, 'event': 'new_graph_connection'})
    

if __name__ == "__main__":
    _, ip, port, id = sys.argv
    socket.connect(f'http://{ip}:{port}')
    nw.start(id)
    send_new_node()
    connect_to_node('A', 20)
    #connect_to_node('B', 20)