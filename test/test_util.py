import os

from link.solve.util import (
        geojson_to_graph,
        make_prox_graph,
        match_solution,
        create_geojson,
        make_assi_graph,
        make_tb_objects,
        make_o_graph
        )

from link.solve.pcst import solve

SIMPLE_INPUT = {"type": "FeatureCollection", "features": [
     {"type": "Feature",
     "geometry": {
         "type": "LineString",
         "coordinates": [
             [18.38724584292816, -34.10317093131459],
             [18.38742811501918, -34.10332185781299]]
     },
     "properties":
         {"node_1": str([18.38987647256616, -34.104647551974494]),
         "node_2": str([18.3901436622786, -34.104491994918384]),
         "length": 25.775978637305705}
     },
     {"type": "Feature",
         "geometry":{
             "type": "LineString",
             "coordinates": [
                 [18.387538414105652, -34.10308825999736],
                 [18.38724584292816, -34.10317093131459]]
             },
     "properties":
         {"node_1": str([18.38987647256616, -34.104647551974494]),
         "node_2": str([18.3901436622786, -34.104491994918384]),
         "length": 33.681673041196234}
     },
     {"type": "Feature",
     "geometry": {
         "type": "Point",
         "coordinates":
            [18.38724584292816, -34.10317093131459]
         },
     "properties":
         {"demand": 1}
     },
     {"type": "Feature",
     "geometry": {
         "type": "Point",
         "coordinates":
            [18.387538414105652, -34.10308825999736],
         },
     "properties":
         {"demand": 1}
     },
     {"type": "Feature",
     "geometry":{
         "type": "Point",
         "coordinates":
             [18.38742811501918, -34.10332185781299],
     },
     "properties":
          {"capacity": 500,
           "candidate": 500}
 }]}

def test_geojson_graph_1():
    in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])

    assert in_graph.nodes()
    assert in_graph.edges()
    assert lines


def test_prox_graph_1():
    in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])
    node_map, prox_graph = make_prox_graph(in_graph)

    assert len(prox_graph.nodes()) == len(in_graph.nodes())
    assert len(prox_graph.edges()) == len(in_graph.edges())
    assert node_map


def test_match_solution():
    in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])
    node_map, prox_graph = make_prox_graph(in_graph)

    s_graph = solve(prox_graph, 1)
    o_graph = match_solution(s_graph, node_map, in_graph, lines, points)

    assert o_graph.edges()


def test_create_geojson():
    in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])
    node_map, prox_graph = make_prox_graph(in_graph)

    s_graph = solve(prox_graph, 1)
    o_graph = match_solution(s_graph, node_map, in_graph, lines, points)

    assert create_geojson(o_graph)


def test_create_assi():
    in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])
    assi_graph, node_map, gt_g, ass_to_path, _, _, _ = make_assi_graph(in_graph)

    assert assi_graph.edges()

if os.environ.get("TBART", False):
    def test_tb_obj():
        in_graph, lines, points = geojson_to_graph(SIMPLE_INPUT['features'])
        assi_graph, node_map, gt_g, _, _, _, _ = make_assi_graph(in_graph)

        # Crete R objects and solve
        r_spatial_df_demand, r_spatial_df_candidates, r_cost_matrix, candidates = make_tb_objects(assi_graph, points, node_map)

        assert candidates.values.tolist()

