import random
import networkx as nx
import numpy as np


#### Restrictions ####


# First restriction
def no_cycles(subgraph):
    """Function to check that a graph does not have cycles"""
    subgraph_undirected = subgraph.to_undirected()
    list_cycles = nx.cycle_basis(subgraph_undirected)
    return len(list_cycles) == 0


# Second restriction
def connected(subgraph):
    """Function to check that graph stays as a single connected component"""
    connected_components = nx.weakly_connected_components(subgraph)
    list_ccs = list(connected_components)
    return len(list_ccs) == 1


# Third restriction
def no_more_than_two_per(subgraph, limit=2):
    """Function to check that a company does not contain more than two human owners"""
    indegrees = [
        subgraph.in_degree(node)
        for node in subgraph.nodes
        if subgraph.nodes[node]["human"]
    ]
    indegrees = np.array(indegrees)
    return not any(indegrees > limit)


# Fourth restriction
def only_human_roots(subgraph):
    """Function to check that a graph only contains human roots"""
    is_human = [
        subgraph.nodes[node]["human"]
        for node in subgraph.nodes
        if subgraph.out_degree(node) == 0
    ]
    return sum(is_human) == len(is_human)


# Fifth restriction
def no_slavery(subgraph):
    """Function to check that a human cannot own share of another human"""
    degrees = sum(
        subgraph.out_degree(node)
        for node in subgraph.nodes
        if subgraph.nodes[node]["human"]
    )
    return degrees == 0


#### Alterations ####


def one_swap(subgraph, change="origin"):
    """
    Function to swap an edge in a given graph.
    By default, we are only changing the source of a link.
    To chance the destination, change='destination'
    """
    subgraph_copy = subgraph.copy()
    edges = list(subgraph_copy.edges)
    idx = np.random.randint(len(edges))
    node1, node2 = edges[idx]
    weight = subgraph.edges[edges[idx]]["weight"]

    other_nodes = [node for node in subgraph_copy.nodes if node not in (node1, node2)]

    if len(other_nodes) > 0:
        node3 = random.choice(other_nodes)
        subgraph_copy.remove_edge(node1, node2)

        if change == "origin":
            subgraph_copy.add_edge(node3, node2, weight=weight)
        elif change == "destination":
            subgraph_copy.add_edge(node1, node3, weight=weight)
        elif change == "random":
            if np.random.rand() < 0.5:
                subgraph_copy.add_edge(node3, node2, weight=weight)
            else:
                subgraph_copy.add_edge(node1, node3, weight=weight)
        else:
            raise TypeError(
                "Variable 'change' can only take values 'origin', 'destination' and 'random'"
            )

    else:
        print("Only two nodes in this graph")

    return subgraph_copy


def check_if_subgraph_passes(subgraph, checks):
    """Function to check if a subgraph passes the given restrictions"""
    passed = []
    for func in checks:
        b = func(subgraph)
        passed.append(b)
    sum_ = sum(passed)

    return sum_ == len(checks)


def get_swapped_subgraph(subgraph, checks, n_tries=100, change="random"):
    """Function that returns a subgraph with an edge swap passing all the checks"""
    n_try = 0
    passing = False
    while n_try < n_tries and not passing:
        swapped_subgraph = one_swap(subgraph, change=change)
        passing = check_if_subgraph_passes(swapped_subgraph, checks)
        n_try += 1
    if n_try > n_tries and not passing:
        return None
    if passing:
        return swapped_subgraph
