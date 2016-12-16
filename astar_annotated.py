# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Salim Fadhley <salimfadhley@gmail.com>
#          Matteo Dell'Amico <matteodellamico@gmail.com>
#
# Annotated by: Liani Lye <liani.lye@students.olin.edu>
"""
Shortest paths and path lengths using the A* algorithm.
"""

from heapq import heappush, heappop
from itertools import count
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['astar_path', 'astar_path_length']


@not_implemented_for('multigraph')
def astar_path(G, source, target, heuristic=None, weight='weight'):
    """
    Outputs a list of nodes in a shortest path between start and end nodes
    using the A* algorithm.  There may be more than one shortest path, but this
    returns only one.
	"""

    # Basic error handling.  If the start and end nodes indicated by the user do
    # not exist in the graph, raise an error.
    if source not in G or target not in G:
        msg = 'Either source {} or target {} is not in G'
        raise nx.NodeNotFound(msg.format(source, target))

    # NetworkX's implementation of A* does not include a heuristic.
    # The default heuristic is h=0 - same as Dijkstra's algorithm
    if heuristic is None:
        def heuristic(u, v):
            return 0

    # These variables track queue priority order.
    push = heappush
    pop = heappop
    c = count()

    # The queue stores the shortest path.
    queue = [(0, next(c), source, 0, None)]


    # This dictionary, named enqueued, tracks the nodes that have yet to be 
    # analyzed.  Analysis involves calculating the node cost.
    enqueued = {}

    # This dictionary, named explored, tracks the nodes we have visited.
    explored = {}

    # While the queue is not empty, run this loop:
    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = pop(queue)

        # If the node we are currently exploring is the end node, 
        # then we have reached the destination! Return the path we've traversed.
        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        # If the node we are currently analyzing has already been visited,
        # then carry on with the algorithm.
        if curnode in explored:
            continue

        # Set the node that we have most recently explored to the node that we
        # were just at.
        explored[curnode] = parent

        # In this loop, we analyze every node that is adjacent to the one we are
        # curently at.  In this loop, each neighboring node is referred to as
        # 'neighbor node.'
        for neighbor, w in G[curnode].items():

        	# If neighbor node has already been explored, then carry on w/ the alg.
            if neighbor in explored:
                continue

            # Set neighbor node's cost.
            # Cost = (cost to reach the neighbor node from the start node) + 
            # 		 (cost to reach the end node from the neighbor node)
            ncost = dist + w.get(weight, 1)

            # If the neighbor node has yet to be visted:
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]

                # then compare the neighbor node's cost to the cost of other 
                # neighbor nodes.  
                # if qcost < ncost, a longer path to neighbor remains
                # enqueued.
                # This means that the neighbor node we are currently looking at
                # is not the cheapest node!
                if qcost <= ncost:
                    continue

            # If the neighbor node is indeed the cheapest node, then add it
            # to the queue!  We are one step closer to the destination!
            else:
                h = heuristic(neighbor, target)
            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

    # If there is no path, then raise the error statement.
    raise nx.NetworkXNoPath("Node %s not reachable from %s" % (source, target))
