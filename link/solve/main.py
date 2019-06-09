"""
Run the main solver interface
"""
import os

from link.solve.util import (
        geojson_to_graph,
        make_prox_graph,
        make_assi_graph,
        make_tb_objects,
        match_solution,
        create_geojson,
        make_o_graph,
        assi_to_path
)

from link.solve.pcst import solve as solve_pcst
from link.solve.pamp import solve as solve_pamp
from link.solve.nfmp import solve as solve_nfmp
from link.solve.spamp import solve as solve_spamp

if os.environ.get("TBART", False):
    from link.solve.pmed import solve as solve_pmed


    def run_pmed(request_json, p=1):
        """
        The way to run the tb solve
        in_graph is the raw graph from the geoJSON
        r_cost_matrix is the distances from each node to each other node
        we are using a cutoff from the input
        """
        in_graph, lines, points = geojson_to_graph(request_json['features'])
        assi_graph, node_map, gt_g, ass_to_path, _, vertices, _ = make_assi_graph(in_graph)

        # Crete R objects and solve
        r_spatial_df_demand, r_spatial_df_candidates, r_cost_matrix, candidates = make_tb_objects(
            assi_graph,
            points,
            node_map
        )

        s_assi_df = solve_pmed(
            r_spatial_df_demand,
            r_spatial_df_candidates,
            metric=r_cost_matrix,
            p=p
        )

        # Make and write output
        o_graph = make_o_graph(
            s_assi_df,
            candidates,
            in_graph,
            points,
            lines,
            node_map,
            gt_g,
            vertices
        )

        footprint = assi_to_path(
            o_graph,
            node_map,
            in_graph,
            lines,
            points,
            ass_to_path
        )

        out_json = create_geojson(footprint)

        return out_json


def run_pcst(request_json, p=1):
    """
    The way to run a pcst solve
    in_graph is the raw graph from the geoJSON
    i_graph is input graph to the solver
    s_graph is solution graph
    o_graph is the geoJSON output graph

    #TODO: Is it a bad idea to reassemble the graph everytime based on the geoemtry. Yeah, but lets get it working and then come up with a sensible data format.
    #TODO: generate consistent node ids - each time we run we relable every lat, lon node with a "id" this is problematic
    """
    in_graph, lines, points = geojson_to_graph(request_json['features'])
    node_map, i_graph = make_prox_graph(in_graph)
    s_graph = solve_pcst(i_graph, p)
    o_graph = match_solution(s_graph, node_map, in_graph, lines, points)
    out_json = create_geojson(o_graph)

    return out_json


def run_pamp(request_json):
    """
    An assignment formulation that ensures that "hub" points do not share are underlying edges as part of a path.
    The inputted graph is used to find potential paths aka assignments.
    These are then inputted into a MIP model and solved using IBM CPLEX.

    This requires that the input data confirm to the following:

    Points - require the following attributes
    demand - [0,1] use 1 if they are to be connected
    candidate - int the distance to which a hub can connect demands
    capacity - the max number of demand to be connected to a hub

    #TODO: test out demand > 1
    #TODO: allow candidate locations to have demand
    #TODO: allow for special demand to be connected above the capacity
    """
    in_graph, lines, points = geojson_to_graph(request_json['features'])
    assi_graph, node_map, gt_g, ass_to_path, arcs_to_parents, _, demand_to_parents = make_assi_graph(in_graph)

    a_sol = solve_pamp(assi_graph, ass_to_path, arcs_to_parents, demand_to_parents)

    o_graph = assi_to_path(
        a_sol,
        node_map,
        in_graph,
        lines,
        points,
        ass_to_path
    )
    out_json = create_geojson(o_graph)

    return out_json


def run_spamp(request_json):
    """
    The base formulation for "pamp". Typically used for unconstrained facility location or job assignment.
    This creates a light weight way to solve the p-median problem.

    The same input requirements hold as for "run_pamp"
    
    #TODO: consolidate formulations and endpoint with "pamp"
    """
    in_graph, lines, points = geojson_to_graph(request_json['features'])
    assi_graph, node_map, gt_g, ass_to_path, arcs_to_parents, _, demand_to_parents = make_assi_graph(in_graph)

    a_sol = solve_spamp(assi_graph, ass_to_path, arcs_to_parents, demand_to_parents)

    o_graph = assi_to_path(
        a_sol,
        node_map,
        in_graph,
        lines,
        points,
        ass_to_path
    )
    out_json = create_geojson(o_graph)

    return out_json


def run_nfmp(request_json):
    """
    A formulation for solving network flow problems on graphs. Assuming that there are source and sink points.
    Currently it is not possible to specifiy the source point.
    But all sink points with demand > 0 will be connected.
    """
    in_graph, lines, points = geojson_to_graph(request_json['features'])
    node_map, i_graph = make_prox_graph(in_graph)
    s_graph = solve_nfmp(i_graph)
    o_graph = match_solution(s_graph, node_map, in_graph, lines, points)
    out_json = create_geojson(o_graph)

    return out_json

