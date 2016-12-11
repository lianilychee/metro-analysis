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
nodes = ['a','b','c','d','e']
G.add_nodes_from(nodes)

edges = {('a','b') : 15,
        ('a','c'):12,
        ('a','d'):4,
        ('c','b'):3,
        ('d','c'):7,
        ('d','e'):6,
        ('e','c'):1}
G.add_edges_from(edges)

# VERIFY
print 'VERIFICATION'
print 'nodes: ', G.number_of_nodes()
print 'edges: ', G.number_of_edges(), '\n'

profiler = start_profiler()

# TEST ALGS
print 'DIJKSTRA: ', (nx.dijkstra_path(G,'a','d'))
print 'A*:       ', (nx.astar_path(G,'a','d'))
print 'Bellman:  ', (nx.bellman_ford(G, 'a'))

end_profiler(profiler)


# # DRAW GRAPH
# pos = nx.spring_layout(G, scale=2)
# edge_labels = nx.get_edge_attributes(G,'weight')
# nx.draw_networkx(G, pos)
# nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
# plt.show()