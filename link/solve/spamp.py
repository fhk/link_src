"""
Path Assignment Mixed-integer Program (PAMP)
Assumes you have a assignment path graph
"""
import os
import itertools
import copy
from datetime import datetime

import networkx as nx
from docplex.mp.model import Model

def solve(graph, ass_to_path, arcs_to_parents, demand_to_parents):
    """
    Solve the assignment network problem
    """
    s_graph = nx.Graph()
    key = os.environ.get('DO_API_KEY', 'local')
    url = os.environ.get('DO_URL', 'local')
    mdl = Model("assi")
    mdl.set_time_limit(1800)
    edge_assi, c_nodes = formulation(
        mdl,
        graph,
        ass_to_path,
        arcs_to_parents,
        demand_to_parents
    )

    s_edges = run_mdl(mdl, edge_assi, c_nodes, url, key)

    for (s, e), v in s_edges.items():
        if v > 0:
            s_graph.add_edge(s, e)
    return s_graph


def formulation(mdl, graph, ass_to_path, arcs_to_parents, demand_to_parents):
    tasks = {j: f'{j}' for j in graph.nodes() if graph.out_degree[j] == 0}
    cands = {i: f'{i}' for i in graph.nodes() if graph.in_degree[i] == 0}
    edges = {(s, e):f"{s}_{e}" for s, e in list(graph.edges())}
    edge_assi = mdl.integer_var_dict(edges, lb=0, ub=mdl.infinity, name='x')
    c_nodes = mdl.integer_var_dict(cands, lb=0, ub=1, name='z')

    # Creating task assignment contraints
    # logging.info("Creating contraint 2")
    for j in tasks:
        mdl.add_constraint(
            mdl.sum(edge_assi[i[0], j] for i in graph.in_edges(j)) == 1
        )

    # Creating idicator to push cost to use minimal amount of hubs
    # logging.info("Creating constraint 3")
    for i in cands:
        mdl.add_constraint(
            mdl.sum(edge_assi[i, j[1]] for j in graph.out_edges(i)) - graph.node[i]['capacity'] * c_nodes[i] <= 0
        )

    mdl.add_constraint(
        mdl.sum(c_nodes[i] for i in cands) == 1
    )

    mdl.minimize(
        mdl.sum(d['cost'] * edge_assi[i, j] for i, j, d in graph.edges(data=True)) +
        mdl.sum(graph.node[i]['cost'] * c_nodes[i] for i in cands)
    )

    return edge_assi, c_nodes


def run_mdl(mdl, p_arcs, c_nodes, url, key, gap=0.00):
    mdl.parameters.mip.tolerances.mipgap = gap

    if url == 'local':
        sol = mdl.solve()
    else:
        sol = mdl.solve(url=url, key=key)

    solve_gap = sol.solve_details.mip_relative_gap
    solve_time = sol.solve_details.time
    date_time = datetime.now()

    with open(f'sassi_gap_time.{date_time}.txt', 'w') as out:
        out.write(f'{solve_gap}_{solve_time}')

    return sol.get_value_dict(p_arcs)

