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

def _bellman_ford(G, source, weight, pred=None, paths=None, dist=None,
                  cutoff=None, target=None):
    
    ## Creates a dictionary named pred if not already present
    if pred is None:
        ## Dictionary to store a list of predecessors of that node
        ## Here, it adds all the source nodes to the dictionary
        pred = {v: [None] for v in source}
    
    ## Creates a dictionary named dist if not already present
    if dist is None:
        ## Dictionary to store distance from source to that node
        ## Here, it adds all the source nodes to the dictionary and 
        ## sets its distance 0 (because it is the source)
        dist = {v: 0 for v in source}

    ## G_succ is a three-level dictionary (where the value of the first 
    ## dictionary is another dictionary whose value is another dictionary) 
    ## where the keys are each node. There is a different structure for directed
    ## vs. undirected graphs. Here only the directed graphs are explained.

    ## If the graph is directed, we use the NetworkX function succ and if the graph 
    ## is not directed, use the NetworkX function adj.
    
    ## In a directed graph, G_succ is a dictionary where each node is a key. 
    ## Each node's dictionary value is another dictionary. If the node isn't connected 
    ## to anything, this dictionary is empty. Otherwise, this dictionary contains a 
    ## dictionary where the keys are the nodes that the original node is connected to. 
    ## The value of these keys is another dictionary.
    G_succ = G.succ if G.is_directed() else G.adj
    ## This value will be used to handle 'infinity' without actually holding a value worth infinity
    inf = float('inf')
    # Total number or vertices in the graph
    n = len(G)


    count = {}

    ## deque is a double-ended queue. In a regular queue, you can add elements in 
    ## the end of the data structure and you can remove elements from the front.
    ## In a deque, you can add and remove from both ends
    q = deque(source)

    ## in_q is a set of all nodes in the deque. Used for easy look up as dequeue 
    ## won't let you look through its elements except for the end elements
    in_q = set(source)

    ## This terminates when there are no more elements in the dequeue
    while q:
        ## Remove the leftmost element in the dequeue
        u = q.popleft()
        ## Also remove that element from the set so that in_q always reflects what is in the dequeue
        in_q.remove(u)

        ## Skip relaxations if any of the predecessors of u is in the queue because in the futer iterations
        ## We will anyway be looking at those predecessor's children and update them then. This is more of 
        ## an efficiency trick than anything to do with Bellman-Ford algorithm
        if all(pred_u not in in_q for pred_u in pred[u]):
            # The current distance of the node from the source. In the future, this value might decrease
            dist_u = dist[u]

            ## loops through dictionaries of each node and their connected nodes
            ## 'v' is the node that the original node ('u') is connected to
            ## 'e' is the dictionary of that node (as described in 'G_succ') which describes the edge weight
            ## If a node is connected to more than one other node, it will have one iteration for each node.
    
            for v, e in G_succ[u].items():

                ## Calculate the new distance from original node 'u' to the node being considered 'v'
                dist_v = dist_u + weight(v, u, e)

                ## cutoff is the depth to stop the search. Only paths of length <= cutoff are returned
                if cutoff is not None:
                    ## If the distance of v is greater than cutoff, stop looking in this direction
                    ## The continue statement continues with the next iteration of the loop
                    if dist_v > cutoff:
                        continue
                                    
                ## target is the ending node for path. 
                if target is not None:
                    ## If the distance of v is greater than target, stop looking in this direction
                    ## The continue statement continues with the next iteration of the loop
                    if dist_v > dist.get(target, inf):
                        continue
                
                ## Keep going in this direction if the distance of v is less than the one currently stored
                if dist_v < dist.get(v, inf):
                    ## If 'v' (child of the original node 'u') is not in deque
                    if v not in in_q:
                        ## Add 'v' to both the deque as well as the set.
                        q.append(v)
                        in_q.add(v)

                        ## Checks the number of times node 'v' has been accessed
                        count_v = count.get(v, 0) + 1
                        ## If that number is higher than the total number of nodes i.e. it is stuck in a loop
                        if count_v == n:
                            ## IT IS A NEGATIVE CYCLE! Raise an error
                            raise nx.NetworkXUnbounded(
                                "Negative cost cycle detected.")
                        ## Else, update the count to the dictionary
                        count[v] = count_v
                    ## Everything in the node looks good so far and all calculations have been made
                    ## So update the dist (distance) dictionary and pred (predecessors) 
                    ## dictionary with possibly new values
                    dist[v] = dist_v
                    pred[v] = [u]
                
                ## Make sure that the dist values for the node match what we expect    
                elif dist.get(v) is not None and dist_v == dist.get(v):
                    ## and then add 'u' as a predecessor of the node 'v'
                    pred[v].append(u)

    ## Check to make sure the above while loop returns a non-null paths
    ## In the next section of code, it calculates the total cost
    if paths is not None:
        ## Here it either chooses the target nodes or all of the nodes (from pred)
        dsts = [target] if target is not None else pred

        ## for each node to be considered
        for dst in dsts:
            
            ## we are constructing a path where the path atlease contains the 
            ## target nodes (from target) or end nodes (from pred)
            path = [dst]
            cur = dst
            
            ## Get the predecessor for the node we are considering
            while pred[cur][0] is not None:
                cur = pred[cur][0]
                ## Append it to the path we are considering 
                path.append(cur)
            
            ## Reverse, so that the source appears first and the target(s) appear later
            path.reverse()
            ## For the node being considered, set the path to be the one we just calculated
            paths[dst] = path
    

    return dist
