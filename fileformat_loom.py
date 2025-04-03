import json

import Network

def read_network_from_loom(filename):
    network = Network.Network()
    with open(filename) as fp:
        edge_staging = [] # don't resolve edges until we have all the nodes
        data = json.load(fp)
        assert data['type'] == "FeatureCollection"
        for feat in data['features']:
            geom = feat['geometry']
            if geom['type']=="Point":
                prop = feat['properties']
                name = prop['id'] # station_id ?
                label = prop.get('station_label','')
                assert isinstance(name,str)
                assert isinstance(label,str)
                x, y = geom['coordinates']
                network.nodes[name] = Network.Node( x, -y, name, label )
            elif geom['type']=="LineString":
                prop = feat['properties']
                s = prop['from']
                t = prop['to']
                edge_staging.append( (s,t) )
        
        for s,t in edge_staging:
            s = network.nodes[s]
            assert isinstance(s,Network.Node)
            t = network.nodes[t]
            assert isinstance(t,Network.Node)
            network.edges.append( add_edge(s,t) )
                
    return network, data

def add_edge(s,t):
    e = Network.Edge(s,t)
    s.edges.append(e)
    t.edges.append(e)
    return e

def export_loom( net, data ):
    # Put the layout from the Network into Loom's filedata,
    # so that when we run loom on it, it has our positions and bends.
    
    scale = 2e-5 # Scale the coordinates to play nice with Loom's assumptions
    for feat in data['features']:
        geom = feat['geometry']
        if geom['type']=="Point":
            prop = feat['properties']
            name = prop['id']
            v = net.nodes[name]
            geom['coordinates'] = [scale*v.pos.x(), -scale*v.pos.y() ]
        if geom['type']=="LineString":
            prop = feat['properties']
            s = net.nodes[ prop['from'] ]
            t = net.nodes[ prop['to'] ]
            geom = feat['geometry']
            bend = []
            for e in s.edges:
                if e.v[0]==t or e.v[1]==t:
                    if e.bend:
                        bend = [[scale*e.bend.x(),-scale*e.bend.y()]]
                        break
            geom['coordinates'] = [[scale*s.pos.x(),-scale*s.pos.y()]]+bend+[[scale*t.pos.x(),-scale*t.pos.y()]]

    with open('render.json','w') as fp:
        json.dump(data,fp)

def render_loom( fname_in, fname_out ):
    import subprocess
    cmd = f"cat {fname_in} | loom | transitmap -l > {fname_out}"
    subprocess.Popen(cmd,shell=True)