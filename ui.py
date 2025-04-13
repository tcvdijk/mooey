from PySide6.QtGui import QColor, QPen, QBrush 

from Network import *

# Some global UI state

hover_node = None
hover_edge = None
hover_empty_port = None

selected_node = None
selected_edge = None

### Pens and brushes

node_pen = QPen( QColor('black'), 5 )
node_brush = QBrush( QColor('white') )

rose_free_pen = QPen( QColor('lightgray'), 2 )
rose_free_brush = QBrush( QColor('white') )

rose_used_pen = QPen( QColor('black'), 2 )
rose_used_brush = QBrush( QColor('lightgray') )

edge_pen = QPen( QColor('black'), 2 )

highlight_brush = QBrush( QColor('orange'))
selected_brush = QBrush( QColor('yellow'))
active_handle_pen = QPen( QColor('black'), 2 )

# Parameters for UI geometry

hover_node_radius = 60
bezier_radius = 20
bezier_cp = 60
rose_radius = 20
handle_radius = 20

def update_params( view_scale ):
    # Set some of the pens widths based on zoom level (so they don't go invisible)
    edge_pen.setWidthF( max(2,0.35/view_scale) )    
    # Set some of the widget scales based on zoom level (so they don't get too small)
    global rose_radius
    rose_radius = max( 20, 15/view_scale )
    global handle_radius
    handle_radius = max( 6, 4/view_scale )