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
    mdl.set_time_limit(30)
    edge_assi, c_nodes, arc_assi = formulation(
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
    arcs_b = {(a, b, c):f"{a}_{b}_{c}" for e in ass_to_path.values() for a, b in e for c in arcs_to_parents[a, b]}
    flip_arcs = {(a, b, c):f"{a}_{b}_{c}" for e in ass_to_path.values() for b, a in e for c in arcs_to_parents[a, b]}
    arcs = {**arcs_b, **flip_arcs}

    edge_assi = mdl.integer_var_dict(edges, lb=0, ub=mdl.infinity, name='x')
    arc_assi = mdl.integer_var_dict(arcs, lb=0, ub=1, name='w')
    c_nodes = mdl.integer_var_dict(cands, lb=0, ub=1, name='z')

    # Creating hub capacity contraints
    # logging.info("Creating constraint 1")
    for i in cands:
        mdl.add_constraint(
            mdl.sum(edge_assi[i, j[1]] for j in graph.out_edges(i)) <= graph.node[i]['capacity']
        )

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
    # Creating idiciator to push edge use of assignment
    for (i, j), all_arcs in ass_to_path.items():
        u_arcs = set(all_arcs)
        mdl.add_constraint(
            len(u_arcs) * edge_assi[i, j] -
            mdl.sum(arc_assi[a, b, i] for a, b in u_arcs) <= 0
        )

    # Non overlap contraints raw
    seen_arcs = set()
    for (a, b, _) in arcs:
        if (a, b) not in seen_arcs:
            seen_arcs.add((a, b))
            seen_arcs.add((b, a))
            mdl.add_constraint(
                mdl.sum(arc_assi[s, e, i] for s, e in [(a, b), (b, a)]for i in arcs_to_parents[a, b]) <= 1)

    mdl.minimize(
        mdl.sum(d['cost'] * edge_assi[i, j] for i, j, d in graph.edges(data=True)) +
        mdl.sum(graph.node[i]['cost'] * c_nodes[i] for i in cands)
    )

    return edge_assi, c_nodes, arc_assi


def run_mdl(mdl, p_arcs, c_nodes, url, key, gap=0.01):
    mdl.parameters.mip.tolerances.mipgap = gap

    if url == 'local':
        sol = mdl.solve()
    else:
        sol = mdl.solve(url=url, key=key)

    solve_gap = sol.solve_details.mip_relative_gap
    solve_time = sol.solve_details.time
    date_time = datetime.now()

    with open(f'assi_gap_time.{date_time}.txt', 'w') as out:
        out.write(f'{solve_gap}_{solve_time}')

    return sol.get_value_dict(p_arcs)

