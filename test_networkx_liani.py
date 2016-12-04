import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()



# ADD NODES & EDGES
nodes_dline = ['riverside', 'waban', 'eliot', 'newton highlands']
edges_dline = [('riverside','waban'),('waban','eliot'),('eliot','newton highlands')]
weights_dline = [2.225, 4.040, 0.431]

G.add_nodes_from(nodes_dline)
G.add_edges_from(edges_dline)

# add weights to edges
i = 0
for e in edges_dline:
    n1, n2 = e[0], e[1]
    G.edge[n1][n2]['weight'] = weights_dline[i]
    i += 1

# VERIFY
print 'nodes: ', G.number_of_nodes()
print 'edges: ', G.number_of_edges()

# Graph setup
pos = nx.spring_layout(G, scale=2)
edge_labels = nx.get_edge_attributes(G,'weight')

# SHOW GRAPH
nx.draw_networkx(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
plt.show()