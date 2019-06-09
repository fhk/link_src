"""
Solve using the prize collecting steiner tree approach.
Utilizes functionality from: https://github.com/fraenkel-lab/pcst_fast
"""

import networkx as nx
import numpy as np
from pcst_fast import pcst_fast

def solve(graph, n, root=-1, algo='strong', loglevel=0):
    """
    Small wrapper around lib.
    Takes a input graph
    Returns a graph
    """
    magic_prize_multi = 10000 # use this to ensure that all required points are connected.
    eds = np.array([e for e in graph.edges()])
    vertices, edges = pcst_fast(
        eds,
        np.array([graph.node[n].get('prize', 0) * magic_prize_multi for n in range(0, len(graph.nodes()))]),
        np.array([d['cost'] for _, _, d in graph.edges(data=True)]),
        root,
        n,
        algo,
        loglevel
    )

    s_graph = nx.Graph()
    s_graph.add_nodes_from(vertices)
    s_graph.add_edges_from(eds[edges])

    return s_graph
