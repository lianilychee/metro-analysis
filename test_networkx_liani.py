import networkx as nx
import matplotlib.pyplot as plt
import cProfile, pstats, StringIO


def start_profiler():
    profiler = cProfile.Profile()
    profiler.enable()
    return profiler

def end_profiler(profiler):
    profiler.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()

G = nx.Graph()


# ADD NODES & EDGES
nodes = ['A', 'B', 'C', 'D']
G.add_nodes_from(nodes)

# add weights to edges
G.add_edge('A', 'B', {'weight':4})
G.add_edge('B', 'D', {'weight':6})

G.add_edge('B', 'C', {'weight':1})

G.add_edge('A', 'C', {'weight':2})
G.add_edge('C', 'D', {'weight':8})

# VERIFY
print 'VERIFICATION'
print 'nodes: ', G.number_of_nodes()
print 'edges: ', G.number_of_edges(), '\n'

profiler = start_profiler()

# TEST ALGS
print 'DIJKSTRA: ', (nx.dijkstra_path(G,'A','D'))
print 'A*:       ', (nx.astar_path(G,'A','D'))
print 'Bellman:  ', (nx.bellman_ford(G, 'A'))

end_profiler(profiler)


# # DRAW GRAPH
# pos = nx.spring_layout(G, scale=2)
# edge_labels = nx.get_edge_attributes(G,'weight')
# nx.draw_networkx(G, pos)
# nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
# plt.show()