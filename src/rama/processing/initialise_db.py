import pandas as pd
import networkx as nx

from rama.src.rama.processing.load_database_pipeline import process_database, get_graph
from rama.src.rama.processing.node_attributes import set_attributes
from rama.src.rama.processing.study_graphs import get_dict_cluster, classify_cluster


def initialise(path, psc_filenames, companies_filenames, string_ownership="ownership-of-shares"):
    """Function to initialise the usual database"""

    list_pscs = []
    for name in psc_filenames:
        psc_dummy = pd.read_csv(path + name)
        list_pscs.append(psc_dummy)

    list_companies = []
    for name in companies_filenames:
        companies_dummy = pd.read_csv(path + name)
        list_companies.append(companies_dummy)

    list_dfs, edge_list = process_database(list_pscs, list_companies, string_ownership)

    companies = list_dfs[0]
    merged_firstlink = list_dfs[1]
    psc_companies = list_dfs[2]

    ### Get graph
    graph = get_graph(edge_list)

    ### Set attributes
    set_attributes(graph, merged_firstlink, psc_companies, companies)

    ### Connected components
    connected_components = list(
        sorted(nx.weakly_connected_components(graph), key=len, reverse=True)
    )

    ### Set attributes to connected components
    dict_cluster = {}
    for number_of_cluster, set_nodes in enumerate(connected_components):
        dict_cluster_unclassified = get_dict_cluster(graph, list(set_nodes))
        dict_cluster[number_of_cluster] = classify_cluster(dict_cluster_unclassified)

    return graph, connected_components, dict_cluster


def initialise_humans(
    path, psc_filenames, companies_filenames, string_ownership="ownership-of-shares"
):
    """Function to initialise and get the graphs with human roots"""
    graph, connected_components, dict_cluster = initialise(
        path, psc_filenames, companies_filenames, string_ownership
    )
    ### get indices where there are humans
    graphs_with_humans = [
        i
        for i in range(len(connected_components))
        if dict_cluster[i]["number_of_humans"] > 0 and dict_cluster[i]["class_int"] > 0
    ]

    return graph, connected_components, graphs_with_humans
