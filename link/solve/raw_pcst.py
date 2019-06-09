"""
Sometimes its just too big so we want to not create a graph.
"""
from collections import defaultdict

import numpy as np

from pcst_fast import pcst_fast

def solve(features, root=-1, algo='strong', loglevel=0):
    n = 1
    node_id = 0
    node_map = defaultdict(int)
    demand = {}
    edges = set()
    edge_cost = {}
    edge_features = {}
    for f in features:
        attributes = f['properties']

        if f['geometry']['type'] == 'Point':
            coord = f['geometry']['coordinates']
            one = coord[0]
            two = coord[1]
            coord_key = f'[{one:.7f}, {two:.7f}]'
            if not node_map.get(coord_key):
                node_map[coord_key] = node_id
                node_id += 1
        if attributes.get('demand', False):
            demand[node_map[coord_key]] = 1
        if f['geometry']['type'] == 'LineString':

            coords = f['geometry']['coordinates']
            l_one = coords[0][0]
            l_two = coords[0][1]
            l_three = coords[1][0]
            l_four = coords[1][1]
            s_coords_string = f'[{l_one:.7f}, {l_two:.7f}]'
            e_coords_string = f'[{l_three:.7f}, {l_four:.7f}]'

            start_node = node_map[s_coords_string]
            end_node = node_map[e_coords_string]

            if not start_node:
                node_map[s_coords_string] = node_id
                start_node = node_id
                node_id += 1
            if not end_node:
                node_map[e_coords_string] = node_id
                end_node = node_id
                node_id += 1
            edge_cost[(start_node, end_node)] = attributes['length']
            if (start_node, end_node) not in edges and (end_node, start_node) not in edges:
                edges.add((start_node, end_node))
            edge_features[(start_node, end_node)] = f
    input_edges = np.array(list(edges))
    edge_nodes = set([s for (s, _) in edges])
    [edge_nodes.add(e) for (_, e) in edges]
    s_vertices, s_edges = pcst_fast(
        input_edges,
        np.array([demand.get(n, 0) * 1000 for n in edge_nodes]),
        np.array([edge_cost[e] for e in edges]),
        root,
        n,
        algo,
        loglevel
    )

    raw = {
        "type": "FeatureCollection",
        "features": []
    }

    for e in input_edges[s_edges]:
        raw['features'].append(edge_features[(e[0], e[1])])


    return raw
