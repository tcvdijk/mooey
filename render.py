from PySide6.QtGui import QColor, QPainterPath, QPen, QFont
from PySide6.QtCore import Qt

from Network import *
from math import sqrt

import ui

diag = 1/sqrt(2) # notational convenience

port_offset = [ QPointF(-1,0)
              , QPointF(-diag,diag)
              , QPointF(0,1)
              , QPointF(diag,diag)
              , QPointF(1,0)
              , QPointF(diag,-diag)
              , QPointF(0,-1)
              , QPointF(-diag,-diag)
              ]

font = QFont("Helvetica", 30, QFont.Bold)

def render_network( painter, net, show_labels ):

    # Coordinate system axes
    painter.setPen(QPen(QColor('lightgray'),10))
    painter.setFont(font)
    painter.drawLine( 0, 0, 100, 0 )
    painter.drawText( 130, 10, "x" )
    painter.drawLine( 0, 0, 0, 100 )
    painter.drawText( 1, 150, "y" )

    # Draw the edges
    for e in net.edges:
        painter.setPen( ui.edge_pen )

        painter.setBrush(Qt.NoBrush )

        a_start = e.v[0].pos
        if e.free_at(e.v[0]):
            if e.v[0]==ui.hover_node: a_1 = free_edge_handle_position(e.v[0],e)
            else: a_1 = e.v[0].pos + (ui.bezier_radius*e.direction(e.v[0])).toPointF()
            a_2 = e.v[0].pos + (ui.bezier_cp*e.direction(e.v[0])).toPointF()
        else:    
            a_1 = e.v[0].pos + ui.bezier_radius*port_offset[e.port[0]]
            a_2 = e.v[0].pos + ui.bezier_cp*port_offset[e.port[0]]

        b_start = e.v[1].pos
        if e.free_at(e.v[1]):
            if e.v[1]==ui.hover_node: b_1 = free_edge_handle_position(e.v[1],e)
            else: b_1 = e.v[1].pos + (ui.bezier_radius*e.direction(e.v[1])).toPointF()
            b_2 = e.v[1].pos + (ui.bezier_cp*e.direction(e.v[1])).toPointF()
        else:    
            b_1 = e.v[1].pos + ui.bezier_radius*port_offset[e.port[1]]
            b_2 = e.v[1].pos + ui.bezier_cp*port_offset[e.port[1]]

        path = QPainterPath()
        if e.free_at(e.v[0]):
            path.moveTo( a_1 )
        else:
            path.moveTo( a_start )
            path.lineTo( a_1 )
        if e.bend is None: path.cubicTo( a_2, b_2, b_1 )
        else:
            path.lineTo( e.bend )
            path.lineTo( b_1 )
        if not e.free_at(e.v[1]):
            path.lineTo( b_start)
        painter.drawPath(path)

    # Draw UI for the node close to the mouse
    if ui.hover_node:
        draw_rose( painter, ui.hover_node )
        for e in ui.hover_node.edges:
            if e.free_at(ui.hover_node):
                painter.setPen( ui.rose_used_pen)
                painter.setBrush( ui.rose_used_brush )
                if e==ui.selected_edge: painter.setBrush( ui.selected_brush )
                if e==ui.hover_edge: painter.setBrush( ui.highlight_brush )
                handle_pos = free_edge_handle_position(ui.hover_node, e)
                painter.drawEllipse(handle_pos,ui.handle_radius,ui.handle_radius)

    # Draw the nodes
    painter.setPen(ui.node_pen)
    painter.setBrush(ui.node_brush)
    for name, v in net.nodes.items():
        painter.drawEllipse(v.pos, 10, 10)
        if show_labels: painter.drawText( v.pos + QPointF(ui.bezier_radius,10), v.name )


def handle_position( v, p ):
    return v.pos + ui.rose_radius*port_offset[p]

def free_edge_handle_position( v, e ):
    dir = e.direction(v).toPointF()
    return v.pos + 2*ui.rose_radius*dir

def is_hovered( v, i ):
    if v!=ui.hover_node: return False
    if v.ports[i] is None and i==ui.hover_empty_port: return True
    return ui.hover_edge is not None and v.ports[i]==ui.hover_edge

def draw_rose( painter, v: Node ):
    ui.rose_free_pen.setCosmetic(True)
    ui.rose_used_pen.setCosmetic(True)
    ui.active_handle_pen.setCosmetic(True)
    for i in range(8):
        if v.ports[i] is None:
            painter.setPen(ui.rose_free_pen)
            painter.setBrush(ui.rose_free_brush)
        else:
            painter.setPen(ui.rose_used_pen)
            painter.setBrush(ui.rose_used_brush)
        if ui.selected_node is not None:
            painter.setPen( ui.active_handle_pen )
        if ui.selected_node==v and ui.selected_edge is not None and ui.selected_edge==v.ports[i]:
            painter.setBrush(ui.selected_brush)
        if is_hovered( v, i ):
            painter.setBrush(ui.highlight_brush)

        painter.drawEllipse( handle_position(v,i), ui.handle_radius, ui.handle_radius )
