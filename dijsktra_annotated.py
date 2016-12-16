# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:  Aric Hagberg <hagberg@lanl.gov>
#           Loïc Séguin-C. <loicseguin@gmail.com>
#           Dan Schult <dschult@colgate.edu>
#           Niels van Adrichem <n.l.m.vanadrichem@tudelft.nl>
"""
Shortest path algorithms for weighed graphs.
"""

from collections import deque
from heapq import heappush, heappop
from itertools import count
import networkx as nx
from networkx.utils import generate_unique_node
import warnings as _warnings

def _dijkstra_multisource(G, sources, weight, pred=None, paths=None,
                          cutoff=None, target=None):
    
    ## G_succ is a three-level dictionary where each node is a key. There is a different structure for directed vs. undirected graphs, but I will explain the directed graphs.
    ## If the graph is directed, we use the NetworkX function succ and if the graph is not directed, use the NetworkX function adj.
    
    ## In a directed graph, G_succ is a dictionary where each node is a key. Each node's dictionary value is another dictionary. If the node isn't connected to anything, this dictionary is empty.
    ## Otherwise, this dictionary contains a dictionary where the keys are the nodes that the original node is connected to. The value of these keys is another dictionary.
    ## See Example 1
    G_succ = G.succ if G.is_directed() else G.adj

    ## Using the heapq package, heappush pushes the specified item into the heap, keeping the order
    push = heappush
    ## Using the heapq package, heappop removes and returns the smallest item in the heap
    pop = heappop

    ## Creating two empty dictionaries to keep track of (1-dist) final distances and
    ## (2-seen) whether the nodes have been seen
    dist = {}  # NX: dictionary of final distances
    seen = {}

    # NX: fringe is heapq with 3-tuples (distance,c,node)
    # NX: use the count c to avoid comparing nodes (may not be able to)

    ## creates a list with the frequency of nodes
    c = count()
    ## creates an empty list to keep track of 3-tuples created later
    fringe = []

    ## loops through each node in the list of nodes that was passed in to the function
    for source in sources:
        ## sets the value for the current node in the array seen to zero
        seen[source] = 0
        ## creates a tuple called fringe with the distance set to zero, the next value from the list 'c' (frequency of nodes), and the node itself and appends it to the dictionary 'fringe'
        push(fringe, (0, next(c), source))

    ## while fringe contains elements, keep looping through the while loop
    while fringe:
        ## removes and returns the last item in the array 'fringe'; sets the distance to d, ignores the middle term, and sets the node/vertex to v
        (d, _, v) = pop(fringe)

        ## if the vertex is already in the final distance array, we have already looked at it, so skip it
        if v in dist:
            continue  # NX: already searched this node.

        ## if the vertex's distance hasn't already been calculated, add an entry to 'dist' with the vertex and its distance
        dist[v] = d

        ## if the vertex is the target (aka the ending vertex that we are looking for), break the while loop because we have found our shortest path
        if v == target:
            break

        ## loops through dictionaries of each node and their connected nodes
        ## 'u' is the node that the original node ('v') is connected to
        ## 'e' is the dictionary of that node (as described in 'G_succ')
        ## If a node is connected to more than one other node, it will have one iteration for each node.
        ## See Example 2
        for u, e in G_succ[v].items():
            ## weight is a "function with (u, v, data) input that returns that edges weight"
            ## sets the cost to the weight between the vertex and its connected node
            cost = weight(v, u, e)
            ## if there is no cost, skip the rest of this
            if cost is None:
                continue
            ## set the distance between v and u to the distance of start -> v plus the cost from v -> u
            vu_dist = dist[v] + cost
            ## Cutoff is "depth to stop the search. Only return paths with length <= cutoff."
            ## If there is a specified cutoff, and the distance from v -> u is larger than the cutoff, skip the rest of this
            if cutoff is not None:
                if vu_dist > cutoff:
                    continue
            ## Loop through each connected node 'u' in the final distance area 'dist'
            if u in dist:
                ## If the distance from 'v' to 'u' is less than the distance to 'u', there is a contradictory path.
                ## There may be negative weights.
                if vu_dist < dist[u]:
                    raise ValueError('Contradictory paths found:',
                                     'negative weights?')

            ## If the connected node 'u' has not been visited or the distance is less than the distance in seen, continue.
            elif u not in seen or vu_dist < seen[u]:
                ## Set the value of seen for 'u' to the distance from 'v' to 'u'
                seen[u] = vu_dist
                ## Add a three-tuple to the array fringe that sets the distance to the distance between 'v' and 'u', the next value from the list 'c', and the connected node 'u'
                push(fringe, (vu_dist, next(c), u))

                ## 'paths' is an optional dictionary to store the distance from the source to each node where the node is the key
                ## If 'None' is passed in where 'paths' should be, it means do not store the paths.
                ## If 'paths' is not 'None,' then store the path to 'u' to be the path to 'v' plus the distance of 'u'
                if paths is not None:
                    paths[u] = paths[v] + [u]

                ## 'pred' is an optional dictionary to store a list of predecessor nodes where the key is the node.
                ## If 'None' is passed in where 'pred' should be, it means do not store the predecessor nodes.
                ## If 'pred' is not 'None,' then store the previous nodes of u to be 'v'
                if pred is not None:
                    pred[u] = [v]
            ## If the distance from 'v' to 'u' is equal to the distance from 'u,' 
            elif vu_dist == seen[u]:
                ## And you want to record the predecessor nodes,
                if pred is not None:
                    ## Add 'v' to the predecessor list of 'u'
                    pred[u].append(v)

    # NX: The optional predecessor and path dictionaries can be accessed by the caller via the pred and paths objects passed as arguments.
    return dist