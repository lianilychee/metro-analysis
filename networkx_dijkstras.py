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

def dijkstra_path(G, source, target, weight='weight'):
    """Returns the shortest weighted path from source to target in G.

    Uses Dijkstra's Method to compute the shortest weighted path
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node

    target : node
       Ending node

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edge[u][v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.

       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number.

    Returns
    -------
    path : list
       List of nodes in a shortest path.

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print(nx.dijkstra_path(G,0,4))
    [0, 1, 2, 3, 4]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The weight function can be used to include node weights.
    ```
    def func(u, v, d):
        return G.node[u].get('node_weight', 1)/2 + \
               G.node[v].get('node_weight', 1)/2 + \
               d.get('weight', 1)
    ```
    In this example we take the average of start and end node
    weights of an edge and add it to the weight of the edge.

    See Also
    --------
    bidirectional_dijkstra(), bellman_ford_path()
    """
    (length, path) = single_source_dijkstra(G, source, target=target,
                                            weight=weight)
    try:
        return path[target]
    except KeyError:
        raise nx.NetworkXNoPath(
            "node %s not reachable from %s" % (target, source))


def dijkstra_path_length(G, source, target, weight='weight'):
    """Returns the shortest weighted path length in G from source to target.

    Uses Dijkstra's Method to compute the shortest weighted path length
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    target : node label
       ending node for path

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edge[u][v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.

       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number.

    Returns
    -------
    length : number
        Shortest path length.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print(nx.dijkstra_path_length(G,0,4))
    4

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    See Also
    --------
    bidirectional_dijkstra(), bellman_ford_path_length()

    """
    if source == target:
        return 0
    weight = _weight_function(G, weight)
    length = _dijkstra(G, source, weight, target=target)
    try:
        return length[target]
    except KeyError:
        raise nx.NetworkXNoPath(
            "Node %s not reachable from %s" % (target, source))

def single_source_dijkstra(G, source, target=None, cutoff=None,
                           weight='weight'):
    """Find shortest weighted paths and lengths from a source node.

    Compute the shortest path length between source and all other
    reachable nodes for a weighted graph.

    Uses Dijkstra's algorithm to compute shortest paths and lengths
    between a source and all other reachable nodes in a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label, optional
       Ending node for path

    cutoff : integer or float, optional
       Depth to stop the search. Only return paths with length <= cutoff.

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edge[u][v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.

       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number.

    Returns
    -------
    distance,path : dictionaries
       Returns a tuple of two dictionaries keyed by node.
       The first dictionary stores distance from the source.
       The second stores the path from the source to that node.


    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length,path=nx.single_source_dijkstra(G,0)
    >>> print(length[4])
    4
    >>> print(length)
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    >>> path[4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Based on the Python cookbook recipe (119466) at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    See Also
    --------
    single_source_dijkstra_path()
    single_source_dijkstra_path_length()
    single_source_bellman_ford()
    """
    return multi_source_dijkstra(G, {source}, cutoff=cutoff, target=target,
                                 weight=weight)

def multi_source_dijkstra(G, sources, target=None, cutoff=None,
                           weight='weight'):
    """Find shortest weighted paths and lengths from a given set of
    source nodes.

    Uses Dijkstra's algorithm to compute the shortest paths and lengths
    between one of the source nodes and the given `target`, or all other
    reachable nodes if not specified, for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a
        single node, then all paths computed by this function will start
        from that node. If there are two or more nodes in the set, the
        computed paths may begin from any one of the start nodes.

    target : node label, optional
       Ending node for path

    cutoff : integer or float, optional
       Depth to stop the search. Only return paths with length <= cutoff.

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edge[u][v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.

       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number.

    Returns
    -------
    distance, path : pair of dictionaries
       Returns a tuple of two dictionaries keyed by node.
       The first dictionary stores distance from one of the source nodes.
       The second stores the path from one of the sources to that node.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> length, path = nx.multi_source_dijkstra(G, {0, 4})
    >>> print(length)
    {0: 0, 1: 1, 2: 2, 3: 1, 4: 0}
    >>> path[1]
    [0, 1]
    >>> path[3]
    [4, 3]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Based on the Python cookbook recipe (119466) at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    Raises
    ------
    ValueError
        If `sources` is empty.

    See Also
    --------
    multi_source_dijkstra_path()
    multi_source_dijkstra_path_length()

    """
    if not sources:
        raise ValueError('sources must not be empty')
    if target in sources:
        return ({target: 0}, {target: [target]})
    weight = _weight_function(G, weight)
    paths = {source: [source] for source in sources}  # dictionary of paths
    dist = _dijkstra_multisource(G, sources, weight, paths=paths,
                                 cutoff=cutoff, target=target)
    return (dist, paths)

def _dijkstra_multisource(G, sources, weight, pred=None, paths=None,
                          cutoff=None, target=None):
    """Uses Dijkstra's algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing
        a single node, then all paths computed by this function will
        start from that node. If there are two or more nodes in this
        iterable, the computed paths may begin from any one of the start
        nodes.

    weight: function
        Function with (u, v, data) input that returns that edges weight

    pred: dict of lists, optional(default=None)
        dict to store a list of predecessors keyed by that node
        If None, predecessors are not stored.

    paths: dict, optional (default=None)
        dict to store the path list from source to each node, keyed by node.
        If None, paths are not stored.

    target : node label, optional
        Ending node for path. Search is halted when target is found.

    cutoff : integer or float, optional
        Depth to stop the search. Only return paths with length <= cutoff.

    Returns
    -------
    distance : dictionary
        A mapping from node to shortest distance to that node from one
        of the source nodes.

    Notes
    -----
    The optional predecessor and path dictionaries can be accessed by
    the caller through the original pred and paths objects passed
    as arguments. No need to explicitly return pred or paths.

    """
    G_succ = G.succ if G.is_directed() else G.adj

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()

    fringe = []
    for source in sources:
        seen[source] = 0
        push(fringe, (0, next(c), source))
    while fringe:
        (d, _, v) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if v == target:
            break
        for u, e in G_succ[v].items():
            cost = weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            if cutoff is not None:
                if vu_dist > cutoff:
                    continue
            if u in dist:
                if vu_dist < dist[u]:
                    raise ValueError('Contradictory paths found:',
                                     'negative weights?')
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u))
                if paths is not None:
                    paths[u] = paths[v] + [u]
                if pred is not None:
                    pred[u] = [v]
            elif vu_dist == seen[u]:
                if pred is not None:
                    pred[u].append(v)

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist

def _weight_function(G, weight):
    """Returns a function that returns the weight of an edge.

    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

    Parameters
    ----------
    G : NetworkX graph.

    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.

    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the eedge joining those nodes. That function returns
        a number representing the weight of an edge.

    If `G` is a multigraph, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.

    """
    if callable(weight):
        return weight
    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if G.is_multigraph():
        return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
    return lambda u, v, data: data.get(weight, 1)

def pairwise(iterable, cyclic=False):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    first = next(b, None)
    if cyclic is True:
        return zip(a, chain(b, (first,)))
    return zip(a, b)

if __name__ == '__main__':
	G = nx.path_graph(10)
	print(dijkstra_path(G,0,4))