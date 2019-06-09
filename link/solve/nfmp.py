"""
Network Flow Mixed-integer Program (NFMP)
Assumes you have a fully connected graph that is the potential path

Based on the paper:
Availiable here:
"""
import os
import logging
from datetime import datetime

import networkx as nx
from docplex.mp.model import Model

def solve(graph):
    """
    Solve the network flow problem
    
    Here you can use either you IBM CPLEX cloud credentials or a local
    version assuming you have set it up.

    # TODO: provide way to set timeout
    # TODO: provide way to set stop gap
    # TODO: provide better logging
    # TODO: output solve log in a better way
    # TODO: parameterize magic unit costs
    """
    s_graph = nx.Graph()
    key = os.environ.get('DO_API_KEY', 'local')
    url = os.environ.get('DO_URL', 'local')
    mdl = Model("flow")
    mdl.set_time_limit(1800)
    edge_flow, c_nodes = formulation(mdl, graph)

    s_edges = run_mdl(mdl, edge_flow, c_nodes, url, key)

    for (s, e), v in s_edges.items():
        if v > 0:
            s_graph.add_edge(s, e)

    return s_graph


def formulation(mdl, graph):
    edges_both_ways = {
        (s, e):f"s_e" for s, e in list(
            graph.edges())}
    candidate_nodes = {
        n:f"n" for n, d in graph.nodes(
            data=True) if d.get('candidate', False)}
    edge_flow = mdl.integer_var_dict(
        edges_both_ways, lb=0, ub=mdl.infinity, name='x')
    edge_use = mdl.integer_var_dict(
        edges_both_ways, lb=0, ub=1, name='w')
    c_nodes = mdl.integer_var_dict(
        candidate_nodes, lb=0, ub=1, name='z')

    # flow into a node should be equal to the flow out such that demand is met
    # logging.info("Creating constraint 1")
    for i, d in graph.nodes(data=True):
        mdl.add_constraint(
            mdl.sum(edge_flow[(i, j)] for j in graph.neighbors(i))
            - mdl.sum(edge_flow[(k, i)] for k in graph.neighbors(i))
            == d.get('demand', 0)
        )

    # logging.info("Creating constraint 2") 
    for i in candidate_nodes:
        mdl.add_constraint(
            mdl.sum(edge_flow[(i, j)] for j in graph.neighbors(i))
            <= c_nodes[i] * graph.node[i].get('capacity', 100)
        )

    # logging.info("Creating constraint 3")
    for s, e in edges_both_ways:
        mdl.add_constraint(
            edge_flow[(s, e)] -  100000 * edge_use[(s, e)] <= 0
        )

    # logging.info("Creating objective")
    mdl.minimize(
        mdl.sum(
            graph.node[i].get('cost', 1000)
            * c_nodes[i] for i in candidate_nodes)
        + 50 * mdl.sum(d['cost'] # magic number cost per distance unit
            * edge_use[(i, j)] for i, j, d in graph.edges(data=True))
    )

    return edge_flow, c_nodes


def run_mdl(mdl, edge_flow, c_nodes, url, key, gap=0.00):
    mdl.parameters.mip.tolerances.mipgap = gap

    if url == 'local':
        sol = mdl.solve()
    else:
        sol = mdl.solve(url=url, key=key)

    solve_gap = sol.solve_details.mip_relative_gap
    solve_time = sol.solve_details.time
    date_time = datetime.now()

    with open(f'flow_gap_time.{date_time}.txt', 'w') as out:
        out.write(f'{solve_gap}_{solve_time}')

    return sol.get_value_dict(edge_flow)

