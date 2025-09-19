from math import inf, sqrt, pi
from time import perf_counter

from Network import *

from mui import logline

from ortools.linear_solver import pywraplp as lp

diag = 1/sqrt(2) # notational convenience

# How long must the distance from station to station be?
# in the "short" and "long" cases?
min_dist = 100
# Factor for how long the distance to bend must be
# in the "short" and "long" cases
bend_short = 0.5
bend_long = 1

def layout_lp( net, stable_node:Node = None ):
    

    start = perf_counter()
    solver = lp.Solver.CreateSolver('GLOP')

    if stable_node:
        # Track where the "stable node" was before
        old_stable_pos = stable_node.pos

    objective = solver.Sum([])
    for v in net.nodes.values():
        v.xvar = solver.NumVar(0,solver.infinity(), v.name+'_x')
        v.yvar = solver.NumVar(0,solver.infinity(), v.name+'_y')

    # Layout constraints and length minimization
    for e in net.edges:
        # Clear bends
        e.bend = None
        # Add direction and distance constraint:
        # - from any assigned endpoint of the edge
        # - or don't, if both sides unassigned
        if e.port[0] is None:
            if e.port[1] is None:
                continue # Unconstrained edge
            else:
                # Edge is assigned at v1
                objective += edge_constraint( solver, objective, e.v[1], e.port[1], e.v[0], min_dist )
        else:
            if e.port[1] is None:
                # Edge is assigned at v0
                objective += edge_constraint( solver, objective, e.v[0], e.port[0], e.v[1], min_dist )
            else:
                # Edge is assigned at both ends; could have a bend
                if e.port[0]==opposite_port(e.port[1]):
                    # No bend; do arbitrary direction
                    objective += edge_constraint( solver, objective, e.v[0], e.port[0], e.v[1], min_dist )
                else:
                    # Bend
                    e.bend = Node(0,0,f"bend-{e.v[0].name}-{e.v[1].name}")
                    e.bend.xvar = solver.NumVar(0,solver.infinity(), v.name+'_x')
                    e.bend.yvar = solver.NumVar(0,solver.infinity(), v.name+'_y')
                    objective += edge_constraint( solver, objective, e.v[0], e.port[0], e.bend, min_dist*bend_length( e, 0 ) )
                    objective += edge_constraint( solver, objective, e.v[1], e.port[1], e.bend, min_dist*bend_length( e, 1 ) )

    # Space the stations on degree 2 paths
    seen = dict()
    for v in net.nodes.values():
        if v in seen: continue
        if is_straight_deg2(v):
            seen[id(v)] = True
            path1 = spacewalk( v.edges[0].other(v), v, seen )
            path2 = spacewalk( v.edges[1].other(v), v, seen )
            walk = path1 + [v] + [v for v in reversed(path2)]
            spacevar = solver.NumVar(0,solver.infinity(),name=f"{v.name}-spacer")
            objective += spacevar
            for a, b in zip(walk,walk[1:]):
                solver.Add( a.xvar-b.xvar <= spacevar )
                solver.Add( b.xvar-a.xvar <= spacevar )
                solver.Add( a.yvar-b.yvar <= spacevar )
                solver.Add( b.yvar-a.yvar <= spacevar )


    # Solve the LP
    solver.Minimize( objective )
    status = solver.Solve()
    if status==lp.Solver.OPTIMAL:
        runtime = perf_counter()-start
        logline( "layout\tLayout LP runtime (s)\t" + str(runtime) )
        print( "Layout LP runtime",perf_counter()-start,"s")
        for v in net.nodes.values():
            v.set_position( v.xvar.solution_value(), v.yvar.solution_value() )
            del(v.xvar)
            del(v.yvar)
        for e in net.edges:
            if e.bend is not None:
                # Bend was a Node for solving; reduce it to a point
                e.bend = QPointF( e.bend.xvar.solution_value(), e.bend.yvar.solution_value() )

        if stable_node is not None: return stable_node.pos - old_stable_pos
        else: return True
    else:
        logline( "stats\tlayout failed with status "+str(status))
        print(status)
        print('OPTIMAL', status==lp.Solver.OPTIMAL)
        print('UNBOUNDED', status==lp.Solver.UNBOUNDED)
        print('INFEASIBLE', status==lp.Solver.INFEASIBLE)
        for v in net.nodes.values():
            del(v.xvar)
            del(v.yvar)
        for e in net.edges:
            e.bend = None # clear bends
        return False


def edge_constraint( solver, objective, a, port, b, min_dist ):
    match port:
        case 0: # W
            solver.Add( a.yvar == b.yvar )
            solver.Add( b.xvar <= a.xvar - min_dist )
            return a.xvar - b.xvar
        case 1: # SW
            solver.Add( a.xvar+a.yvar == b.xvar+b.yvar )
            solver.Add( b.xvar <= a.xvar - diag*min_dist )
            return 2*diag*a.xvar - 2*diag*b.xvar
        case 2: # S
            solver.Add( a.xvar == b.xvar )
            solver.Add( b.yvar >= a.yvar + min_dist )
            return b.yvar - a.yvar
        case 3: # SE
            solver.Add( a.xvar-a.yvar == b.xvar-b.yvar )
            solver.Add( b.xvar >= a.xvar + diag*min_dist )
            return 2*diag*b.xvar - 2*diag*a.xvar
        case 4: # E
            solver.Add( a.yvar == b.yvar )
            solver.Add( b.xvar >= a.xvar + min_dist )
            return b.xvar - a.xvar
        case 5: # NE
            solver.Add( a.xvar+a.yvar == b.xvar+b.yvar )
            solver.Add( b.xvar >= a.xvar + diag*min_dist )
            return 2*diag*b.xvar - 2*diag*a.xvar
        case 6: # N
            solver.Add( a.xvar == b.xvar )
            solver.Add( b.yvar <= a.yvar - min_dist )
            return a.yvar - b.yvar
        case 7: # NW
            solver.Add( a.xvar-a.yvar == b.xvar-b.yvar )
            solver.Add( b.xvar <= a.xvar - diag*min_dist )
            return 2*diag*a.xvar - 2*diag*b.xvar

long_bends = { (1,1), (2,1), (3,1)
             , (1,2), (2,2)
             , (3,1)
             , (7,1)
             }
def bend_length( e, i ):
    #return bend_long
    vertex_free = free_angle( e.v[i], e.port[i] )
    bend_free = bend_angle( e.port[0], e.port[1] )
    is_long = (bend_free,vertex_free) in long_bends
    return bend_long if is_long else bend_short

def free_angle( v, p ):
    return min( num_free_ports(v,p,1), num_free_ports(v,p,-1) )

def num_free_ports( v, p, step ):
    p = (p+step)%8
    free = 1
    while v.ports[p] is None and free<8:
        p = (p+step)%8
        free += 1
    return free

def bend_angle( p, q ):
    return min( (p-q)%8, (q-p)%8 )


def is_straight_deg2(v):
    return len(v.edges)==2 and v.edges[0].port_at(v)==opposite_port(v.edges[1].port_at(v))

def spacewalk( v, prev, seen ):
    # Find maximal degree 2 path for spacer variable
    seen[v] = True
    walk = []
    if is_straight_deg2(v):
        # degree 2, straight through, no bends
        v0 = v.edges[0].other(v)
        v1 = v.edges[1].other(v)
        next = v0 if v1==prev else v1
        if not id(next) in seen:
            walk = spacewalk( next, v, seen )
    walk.append(v)
    return walk
        
