"""
Utils to take the raw request data and package it to run solvers
"""
import os

from collections import defaultdict

from shapely.geometry import LineString, Point
from shapely import ops
import networkx as nx
import pandas as pd

# import osmnx # can be used to simplify a graph

# If using tbart R package check env var
if os.environ.get('TBART', False):

    from rpy2.robjects.packages import importr
    from rpy2.robjects import r, pandas2ri, IntVector

    from graph_tool.topology import shortest_path, shortest_distance

    sp = importr("sp")
    base = importr("base")
    tbart = importr("tbart")

    pandas2ri.activate()

if os.environ.get("GT", False):
    from link.solve.nx2gt import nx2gt


def geojson_to_graph(features):
    """
    assemble the graph from the request data
    """
    in_graph = nx.MultiDiGraph()
    lines = {}
    points = {}
    for f in features:
        attributes = f['properties']
        if f['geometry']['type'] == 'Point':
            coord = f['geometry']['coordinates']
            one = coord[0]
            two = coord[1]
            coord_string = f'[{one:.7f}, {two:.7f}]'
            points[coord_string] = Point(coord)
            attributes['x'] = coord[0]
            attributes['y'] = coord[1]
            in_graph.add_node(coord_string, **attributes)
        if f['geometry']['type'] == 'LineString':
            coords = f['geometry']['coordinates']
            l_one = coords[0][0]
            l_two = coords[0][1]
            l_three = coords[1][0]
            l_four = coords[1][1]
            s_coords_string = f'[{l_one:.7f}, {l_two:.7f}]'
            e_coords_string = f'[{l_three:.7f}, {l_four:.7f}]'
            lines[
                f'[{s_coords_string}, {e_coords_string}]'] = LineString(coords)
            lines[
                f'[{e_coords_string},{s_coords_string}]'] = LineString(coords)

            in_graph.add_edge(
                s_coords_string, e_coords_string, **attributes)
            in_graph.node[s_coords_string]['x'] = coords[0][0]
            in_graph.node[s_coords_string]['y'] = coords[0][1]
            in_graph.node[e_coords_string]['x'] = coords[1][0]
            in_graph.node[e_coords_string]['y'] = coords[1][1]

            in_graph.add_edge(
                    e_coords_string, s_coords_string, **attributes)
            in_graph.node[s_coords_string]['x'] = coords[0][0]
            in_graph.node[s_coords_string]['y'] = coords[0][1]
            in_graph.node[e_coords_string]['x'] = coords[1][0]
            in_graph.node[e_coords_string]['y'] = coords[1][1]

            if s_coords_string not in points.keys():
                points[s_coords_string] = Point(coords[0])

            if e_coords_string not in points.keys():
                points[e_coords_string] = Point(coords[1])
    
    in_graph = [g for g in nx.connected_component_subgraphs(in_graph.to_undirected())][0].to_directed()
    # sin_graph = osmnx.simplify.simplify_graph(in_graph)

    return in_graph, lines, points


def make_prox_graph(in_graph):
    """
    Solving doesnt like tuple nodes so lets clean them
    """
    prox_graph = nx.MultiDiGraph()
    node_map = {}
    for i, n in enumerate(in_graph.nodes()):
        node_map[i] = n

    flip = {v: k for k, v in node_map.items()}
    tot_demand = - sum([d.get('demand', 0) for _, d in in_graph.nodes(data=True)])


    for i, j, d in in_graph.edges(data=True):
        prox_graph.add_edge(flip[i], flip[j], cost=d.get('length', 0))
    for n, d in prox_graph.nodes(data=True):
        if in_graph.node[node_map[n]].get("demand", False):
            prox_graph.node[n]['prize'] = 1.
            prox_graph.node[n]['demand'] = in_graph.node[node_map[n]]["demand"]

        if in_graph.node[node_map[n]].get("candidate", False):
            prox_graph.node[n]['candidate'] = in_graph.node[node_map[n]]["candidate"]

            prox_graph.node[n]['demand'] = tot_demand

    return node_map, prox_graph


def make_assi_graph(in_graph):
    """
    For problem types that expect that connection exist as a path from demand to
    candidate rather than edge to edge.
    """
    ass_graph = nx.DiGraph()
    cands = [n for n, d in in_graph.nodes(data=True) if d.get('candidate', False)]
    demands = [n for n, d in in_graph.nodes(data=True) if d.get('demand', False)]
    node_map, p_graph = make_prox_graph(in_graph)
    flip_node_map = {v: k for k, v in node_map.items()}
    gt_g = None
    ass_to_path = defaultdict(list)
    demand_to_parents = defaultdict(set)
    vertices = None
    # Will work if you have graph-tool installed and GT env variable set to 1
    if os.environ.get("GT", False):
        gt_g, vertices = nx2gt(p_graph)
        f_vertices = {v: k for k, v in vertices.items()}
        pred_map = gt_g.vertex_index.copy()
        shortest_d = shortest_distance(
            gt_g,
            weights=gt_g.ep.cost,
        )
    else:
        shortest_d = nx.shortest_path(p_graph, weight="length")
    
    arcs_to_parents = defaultdict(set)
    for c in cands:
        ass_graph.add_node(
            flip_node_map[c],
            candidate=True,
            capacity=in_graph.node[c]['capacity'],
            cost=in_graph.node[c].get('cost', 1000))
        for d in demands:
            if os.environ.get("GT", False):
                length = shortest_d[
                    gt_g.vertex(vertices[flip_node_map[c]])][
                            int(vertices[flip_node_map[d]])]
            else:
                complete = shortest_d[flip_node_map[c]][flip_node_map[d]]
                this_path = [(complete[i], complete[i + 1]) for i in range(len(complete) - 1)]
                length = sum(
                        [p_graph.get_edge_data(pn_hop[0], pn_hop[1])[0]['cost'] for pn_hop in this_path])
                id_map = None
            if length <= in_graph.node[c]['candidate']:
                if os.environ.get("GT", False):
                    _, this_path = shortest_path(
                        gt_g,
                        source=vertices[flip_node_map[c]],
                        target=vertices[flip_node_map[d]],
                        weights=gt_g.ep.cost
                    )

                    id_map = gt_g.vp["id"]

                ass_graph.add_edge(
                        flip_node_map[c],
                        flip_node_map[d],
                        length=length,
                        cost=length) # TODO: should be handled better
                ass_graph.node[flip_node_map[d]]['demand'] =  True

                for (a, b) in this_path:
                    start_n = a
                    end_n = b
                    if os.environ.get("GT", False):
                        start_n = int(id_map[gt_g.vertex(a)])
                        end_n = int(id_map[gt_g.vertex(b)])
                    
                    ass_to_path[(
                        flip_node_map[c],
                        flip_node_map[d])].append((start_n, end_n))
                    arcs_to_parents[start_n, end_n].add(flip_node_map[c])
                    arcs_to_parents[end_n, start_n].add(flip_node_map[c])

                if not this_path:
                    ass_to_path[(
                        flip_node_map[c],
                        flip_node_map[d])].append((c, d))
                    arcs_to_parents[c, d].add(flip_node_map[c])
                    arcs_to_parents[d, c].add(flip_node_map[c])

                demand_to_parents[flip_node_map[d]].add(flip_node_map[c])

    return ass_graph, node_map, gt_g, ass_to_path, arcs_to_parents, vertices, demand_to_parents


def make_tb_objects(assi_graph, points, node_map):
    c_nodes = [n for n, d in assi_graph.nodes(data=True) if d.get('candidate', False)]
    d_nodes = [n for n, d in assi_graph.nodes(data=True) if d.get('demand', False)]

    d_df = pandas2ri.py2ri(pd.DataFrame({"id": d_nodes}))
    candidates = pd.DataFrame({"id": c_nodes})
    c_df = pandas2ri.py2ri(candidates)

    d_coords = pandas2ri.py2ri(pd.DataFrame({
        "lat": [points[node_map[d]].x for d in d_nodes],
        "lon": [points[node_map[d]].y for d in d_nodes]
    }))

    c_coords = pandas2ri.py2ri(pd.DataFrame({
        "lat": [points[node_map[d]].x for d in c_nodes],
        "lon": [points[node_map[d]].y for d in c_nodes]}))

    d_points = sp.SpatialPoints(
       d_coords,
       proj4string=sp.CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"))

    c_points = sp.SpatialPoints(
       c_coords,
       proj4string=sp.CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"))

    d_sdf = sp.SpatialPointsDataFrame(
        d_points,
        d_df
        )

    c_sdf = sp.SpatialPointsDataFrame(
        c_points,
        c_df
        )

    lengths = {'%s_%s'% (i, j): d['length'] for i, j, d in assi_graph.edges(data=True)}

    m = r.matrix(IntVector(
        [lengths.get('%s_%s'% (i, j), 1000) for i in c_nodes for j in d_nodes]),
        nrow=len(d_nodes))

    return d_sdf, c_sdf, m, candidates


def match_solution(s_graph, node_map, in_graph, lines, points):
    """
    Lets reverse out the geometry from the origional graph
    """
    o_graph = nx.Graph()
    for n in s_graph.nodes():
        o_graph.add_node(
                node_map[n],
                geometry=points[node_map[n]]
    )
    for s, e in s_graph.edges():
        geom = lines.get('[%s, %s]'%(node_map[s], node_map[e]), None)
        if geom is None:
            geom = lines.get('[%s, %s]'%(node_map[e], node_map[s]), None)
        if geom is None:
            if (node_map[s], node_map[e]) in in_graph.edges():
                geoms = [g['geometry'] for g in in_graph[node_map[s]][node_map[e]].values()]
            else:
                geoms = [g['geometry'] for g in in_graph[node_map[e]][node_map    [s]].values()]
            for g in geoms:
                coords = g.coords[:]
                o_graph.add_edge(
                    coords[0],
                    coords[1],
                    geometry=g
                )

        else:
            o_graph.add_edge(
                node_map[s],
                node_map[e],
                geometry=geom,
            )
    return o_graph


def create_geojson(o_graph):
    raw = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    i = 0
    for n, d in o_graph.nodes(data=True):
        feat = d.get('geometry', None)
        coords = n
        if feat:
            coords = feat.coords[0]
        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords
            },
            "properties": {
                "id": i
            }
        }

        raw['features'].append(point_feature)
        i += 1

    for s, _, d in o_graph.edges(data=True):
        line_feature = {
            "type": "Feature",
            "geometry": {
            "type": "LineString",
            "coordinates": d['geometry'].coords[:]
            },
            "properties": {
                "id": s
            }
        }

        raw['features'].append(line_feature)
        i += 1

    return raw


def make_o_graph(
    pan_df,
    can_df,
    in_graph,
    points,
    lines,
    node_map,
    gt_g,
    vertices
    ):
    flip_node_map = {v: k for k, v in node_map.items()}
    edges = set()
    for idx, row in pan_df.iterrows():
        # Might hit issues here with larger graphs as each time shortest path is called it explores the graph
        # TODO: So we are going to use all paths, which also takes some time but faster in long run.
        # TODO: Should store these earlier when we compute the paths.

        source = int(row['id'])
        target = can_df.loc[row['allocation'] - 1].id # -1 as R index starts at 1

        edges.add((source, target))

    o_graph = nx.Graph()
    for s, e in edges:
        o_graph.add_edge(s, e, geometry=LineString([points[node_map[s]], points[node_map[e]]]))

    for n in o_graph.nodes():
        o_graph.node[n]['geometry'] = Point(points[node_map[n]])

    return o_graph


def assi_to_path(sol, node_map, graph, lines, points, ass_to_path):
    all_the_edges = nx.Graph()
    coord_to_node = {v: k for k, v in node_map.items()}
    for s, e in sol.edges():
        if not ass_to_path[s, e] and not ass_to_path[e, s]:
            all_the_edges.add_edge(
                s,
                e,
                geometry=LineString([
                    points[s].coords[0],
                    points[e].coords[0]
                ])
            )

            all_the_edges.node[s]['geometry'] = points[s]
            all_the_edges.node[e]['geometry'] = points[e]

        else:
            the_path = ass_to_path[s, e]
            if not the_path:
                the_path = ass_to_path[e, s]
            for s_s, e_e in the_path:
                all_the_edges.add_edge(
                    node_map[s_s],
                    node_map[e_e],
                    geometry=LineString([
                        points[node_map[s_s]].coords[0],
                        points[node_map[e_e]].coords[0]
                    ])
                )

                all_the_edges.node[node_map[s_s]]['geometry'] = points[node_map[s_s]]
                all_the_edges.node[node_map[e_e]]['geometry'] = points[node_map[e_e]]

    return all_the_edges

