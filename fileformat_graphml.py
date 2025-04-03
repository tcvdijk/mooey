import xml.etree.ElementTree as ET

import Network

def read_network_from_graphml(filename):
    network = Network.Network()
    tree = ET.parse(filename)
    root = tree.getroot()

    # Get the nodes
    for node in root.iter('node'):
        name = node.get('id')
        x = -1
        y = -1
        for data in node:   
            if data.tag=='data' and data.get('key')=='x': x = float(data.text)
            if data.tag=='data' and data.get('key')=='y': y = -float(data.text)
            if data.tag=='data' and data.get('key')=='label': label = data.text
        network.nodes[name] = Network.Node( x, y, name, label )

    # Get the edges
    for edge in root.iter('edge'):
        s = network.nodes[edge.get('source')]
        t = network.nodes[edge.get('target')]
        network.edges.append( add_edge(s,t) )

    return network

def add_edge(s,t):
    e = Network.Edge(s,t)
    s.edges.append(e)
    t.edges.append(e)
    return e