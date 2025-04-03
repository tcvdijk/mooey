from math import inf, atan2, pi

from PySide6.QtCore import QPointF
from PySide6.QtGui import QVector2D

def opposite_port( p ):
    return (p+4)%8

class Network:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def scale_by_shortest_edge( self, lb ):
        min_length = min([ e.geo_vector(e.v[0]).length() for e in self.edges ])
        factor = lb/min_length
        for v in self.nodes.values():
            v.pos = factor * v.pos
            v.geo_pos = factor * v.geo_pos

    def evict_all_edges(self):
        for v in self.nodes.values():
            for e in v.edges:
                v.try_evict(e)

class Node:
    def __init__(self, x, y, name: str, label:str = "" ):
        self.pos = QPointF(x,y)
        self.geo_pos = self.pos
        self.name = name
        self.label = label
        self.edges = []
        self.ports = [None]*8

    # def __scopy__(self):
    #     new = Node(0,0,self.name)
    #     new.pos = self.pos
    #     new.geo_pos = self.geo_pos
    #     new.label = self.label
    #     new.edges = [ e for e in self.edges ]
    #     new.ports = [ p for p in self.ports ]
    #     return new


    def set_position( self, x, y ):
        self.pos = QPointF(x,y)

    def neighbors(self):
        return [e.other(self) for e in self.edges]
    
    def sort_edges_by_geo(self):
        self.edges.sort(key=lambda e: e.geo_angle(self))
    def sort_edges(self):
        self.edges.sort(key=lambda e: e.angle(self))


    def assign(self, e, i, force=False) -> bool:
        if self.ports[i] is not None:
            if force: self.evict(self.ports[i])
            else: return False
        me = e.id(self)
        old_port = e.port[me]
        if old_port is not None: self.ports[old_port] = None
        e.port[me] = i
        self.ports[i] = e
        return True
    
    def assign_both_ends( self, e, i, force=False ):
        self.assign(e,i,force)
        e.other(self).assign( e, opposite_port(i), force )

    def evict( self, e ):
        me = e.id(self)
        assert self.ports[e.port[me]] == e
        self.ports[e.port[me]] = None
        e.port[me] = None
        e.bend = None

    def try_evict( self, e ):
        if not e.free_at(self): self.evict(e)


    def straighten_deg2( self, e ):
        port = e.port[e.id(self)]
        v = e.other(self)
        while len(v.edges)==2:
            if v==self: break # loop?
            prev_e = e
            e = v.edges[0] if v.edges[0]!=prev_e else v.edges[1]
            v.assign_both_ends(e,port,force=True)
            v = e.other(v)

    def is_right_angle( self ):
        if len(self.edges)==2:
            a = self.edges[0].port_at(self)
            b = self.edges[1].port_at(self)
            return (a+2)%8==b or (b+2)%8==a
        else: return False

    def smoothen( self ):
        if self.is_right_angle():
            a = self.edges[0].port_at(self)
            b = self.edges[1].port_at(self)
            if (a+2)%8==b: a = (a-1)%8
            else: a = (a+1)%8
            self.assign(self.edges[0],a)
            self.assign(self.edges[1],opposite_port(a))
        else: return False


class Edge:
    def __init__(self, a, b):
        self.v = [a,b]
        self.port = [None,None]
        self.bend = None
    
    def id(self,v):
        if self.v[0]==v: return 0
        if self.v[1]==v: return 1
        assert False
    def other(self, v):
        if self.v[0]==v: return self.v[1]
        if self.v[1]==v: return self.v[0]
        assert False
    def port_at(self, v):
        if self.v[0]==v: return self.port[0]
        if self.v[1]==v: return self.port[1]
        assert False

    def free_at(self,v):
        return self.port[self.id(v)]==None

    def direction(self,v):
        return QVector2D(self.v[1-self.id(v)].pos - v.pos).normalized()
    def geo_direction(self,v):
        return QVector2D(self.v[1-self.id(v)].geo_pos - v.geo_pos).normalized()
    
    def vector(self,v):
        return QVector2D(self.v[1-self.id(v)].pos - v.pos)
    def geo_vector(self,v):
        return QVector2D(self.v[1-self.id(v)].geo_pos - v.geo_pos)

    # CCW angles, start at 0 = left
    def angle(self,v):
        dir = self.vector(v)
        return pi-atan2(dir.y(),dir.x())
    def geo_angle(self,v):
        dir = self.geo_vector(v)
        return pi-atan2(dir.y(),dir.x())
    
def round_angle_to_port(angle):
    return int(((angle+pi/8)%(2*pi))/(pi/4))