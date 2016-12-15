def bellman_ford_predecessor_and_distance(G, source, target=None, cutoff=None, weight='weight'):
    """Compute shortest path lengths and predecessors on shortest paths
    in weighted graphs.

    The algorithm has a running time of O(mn) where n is the number of
    nodes and m is the number of edges.  It is slower than Dijkstra but
    can handle negative edge weights.

    Parameters
    ----------
    G : NetworkX graph
       The algorithm works for all types of graphs, including directed
       graphs and multigraphs.

    source: node label
       Starting node for path

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
    pred, dist : dictionaries
       Returns two dictionaries keyed by node to predecessor in the
       path and to the distance from the source respectively.

    Raises
    ------
    NetworkXUnbounded
       If the (di)graph contains a negative cost (di)cycle, the
       algorithm raises an exception to indicate the presence of the
       negative cost (di)cycle.  Note: any negative weight edge in an
       undirected graph is a negative cost cycle.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(5, create_using = nx.DiGraph())
    >>> pred, dist = nx.bellman_ford_predecessor_and_distance(G, 0)
    >>> sorted(pred.items())
    [(0, [None]), (1, [0]), (2, [1]), (3, [2]), (4, [3])]
    >>> sorted(dist.items())
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

    >>> from nose.tools import assert_raises
    >>> G = nx.cycle_graph(5, create_using = nx.DiGraph())
    >>> G[1][2]['weight'] = -7
    >>> assert_raises(nx.NetworkXUnbounded, \
                      nx.bellman_ford_predecessor_and_distance, G, 0)

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The dictionaries returned only have keys for nodes reachable from
    the source.

    In the case where the (di)graph is not connected, if a component
    not containing the source contains a negative cost (di)cycle, it
    will not be detected.

    """
    if source not in G:
        raise nx.NodeNotFound("Node %s is not found in the graph" % source)
    weight = _weight_function(G, weight)
    if any(weight(u, v, d) < 0 for u, v, d in G.selfloop_edges(data=True)):
        raise nx.NetworkXUnbounded("Negative cost cycle detected.")

    dist = {source: 0}
    pred = {source: [None]}

    if len(G) == 1:
        return pred, dist

    weight = _weight_function(G, weight)
        
    return (pred, _bellman_ford(G, [source], weight,pred=pred, dist=dist, cutoff=cutoff, target=target))


def _bellman_ford(G, source, weight, pred=None, paths=None, dist=None,
                  cutoff=None, target=None):
    """Relaxation loop for Bellman–Ford algorithm

    Parameters
    ----------
    G : NetworkX graph
    
    source: list
        List of source nodes

    weight : function
       The weight of an edge is the value returned by the function. The
       function must accept exactly three positional arguments: the two
       endpoints of an edge and the dictionary of edge attributes for
       that edge. The function must return a number.

    pred: dict of lists, optional (default=None)
        dict to store a list of predecessors keyed by that node
        If None, predecessors are not stored

    paths: dict, optional (default=None)
        dict to store the path list from source to each node, keyed by node
        If None, paths are not stored

    dist: dict, optional (default=None)
        dict to store distance from source to the keyed node
        If None, returned dist dict contents default to 0 for every node in the
        source list

    cutoff: integer or float, optional
        Depth to stop the search. Only paths of length <= cutoff are returned
        
    target: node label, optional
        Ending node for path. Path lengths to other destinations may (and
        probably will) be incorrect.

    Returns
    -------
    Returns two dictionaries keyed by node to predecessor in the
       path and to the distance from the source respectively.

    Raises
    ------
    NetworkXUnbounded
       If the (di)graph contains a negative cost (di)cycle, the
       algorithm raises an exception to indicate the presence of the
       negative cost (di)cycle.  Note: any negative weight edge in an
       undirected graph is a negative cost cycle
    """

    if pred is None:
        pred = {v: [None] for v in source}
    
    if dist is None:
        dist = {v: 0 for v in source}

    G_succ = G.succ if G.is_directed() else G.adj
    inf = float('inf')
    n = len(G)

    count = {}
    q = deque(source)
    in_q = set(source)
    while q:
        u = q.popleft()
        in_q.remove(u)

        # Skip relaxations if any of the predecessors of u is in the queue.
        if all(pred_u not in in_q for pred_u in pred[u]):
            dist_u = dist[u]
            for v, e in G_succ[u].items():
                dist_v = dist_u + weight(v, u, e)

                if cutoff is not None:
                    if dist_v > cutoff:
                        continue
                                    
                if target is not None:
                    if dist_v > dist.get(target, inf):
                        continue
                    
                if dist_v < dist.get(v, inf):
                    if v not in in_q:
                        q.append(v)
                        in_q.add(v)
                        count_v = count.get(v, 0) + 1
                        if count_v == n:
                            raise nx.NetworkXUnbounded(
                                "Negative cost cycle detected.")
                        count[v] = count_v
                    dist[v] = dist_v
                    pred[v] = [u]
                    
                elif dist.get(v) is not None and dist_v == dist.get(v):
                    pred[v].append(u)

    if paths is not None:
        dsts = [target] if target is not None else pred
        for dst in dsts:
        
            path = [dst]
            cur = dst
            
            while pred[cur][0] is not None:
                cur = pred[cur][0]
                path.append(cur)
            
            path.reverse()
            paths[dst] = path
    

    return dist
