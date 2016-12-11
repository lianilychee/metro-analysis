from __future__ import print_function, division

# get_ipython().magic(u'matplotlib inline')

import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt

import networkx as nx
import numpy as np

# colors from our friends at http://colorbrewer2.org
COLORS = ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462',
          '#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f']

G = nx.DiGraph()
nodes = ['a','b','c','d','e']
G.add_nodes_from(nodes)
# G.nodes()

edges = {('a','b') : 15,
        ('a','c'):12,
        ('a','d'):4,
        ('c','b'):3,
        ('d','c'):7,
        ('d','e'):6,
        ('e','c'):1}
G.add_edges_from(edges)
# G.edges()

nx.draw_circular(G, 
                 node_color=COLORS[0], 
                 node_size=2000, 
                 with_labels=True)
plt.axis('equal')

