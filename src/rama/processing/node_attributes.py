import networkx as nx
import numpy as np
import pandas as pd

from rama.processing.lists import types_of_ownership


# Main function


def set_attributes(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> None:
    """Function that sets the attributes described in this script to the graph."""
    human_dict = attr_human(graph, merged_firstlink)
    leaf_dict = attr_leaf(graph, merged_firstlink, psc_companies)
    name_dict = attr_name(graph, merged_firstlink, psc_companies)
    kind_dict = attr_kind(graph, merged_firstlink, psc_companies)
    company_numbers_dict = attr_company_numbers(graph, merged_firstlink, psc_companies, companies)
    date_of_creation_dict = attr_date_of_creation(graph, merged_firstlink, psc_companies, companies)
    sic_dict = attr_sic_codes(graph, merged_firstlink, psc_companies, companies)
    country_dict, postal_code_dict = attr_address(graph, merged_firstlink, psc_companies, companies)
    ownership_dict = get_nature_of_ownership_dict(merged_firstlink, psc_companies)

    dict_indegree = dict([(node, in_degree) for (node, in_degree) in graph.in_degree])
    dict_outdegree = dict([(node, out_degree) for (node, out_degree) in graph.out_degree])

    nx.set_node_attributes(graph, human_dict, "human")
    nx.set_node_attributes(graph, leaf_dict, "leaf")
    nx.set_node_attributes(graph, name_dict, "name")
    nx.set_node_attributes(graph, company_numbers_dict, "company_number")
    nx.set_node_attributes(graph, date_of_creation_dict, "date_of_creation")
    nx.set_node_attributes(graph, kind_dict, "kind")
    nx.set_node_attributes(graph, sic_dict, "sic_codes")
    nx.set_node_attributes(graph, country_dict, "country")
    nx.set_node_attributes(graph, postal_code_dict, "postal_code")

    nx.set_edge_attributes(graph, ownership_dict, "ownership")

    dict_weights = get_weight_dict(graph)
    nx.set_edge_attributes(graph, dict_weights, "weight")

    nx.set_node_attributes(graph, dict_indegree, "in_degree")
    nx.set_node_attributes(graph, dict_outdegree, "out_degree")


# Auxiliary functions
def get_company_numbers(
    psc_companies: pd.DataFrame, df_attr: pd.DataFrame, companies: pd.DataFrame
) -> pd.DataFrame:
    """Returns the company numbers of companies only placed on the first column of psc_companies"""
    indices_to_look = psc_companies.idx_company.unique()
    indices_to_look = list(set(indices_to_look).symmetric_difference(set(df_attr.index.unique())))
    indices_to_look = list(map(int, indices_to_look))

    company_names = psc_companies.loc[
        psc_companies.idx_company.isin(indices_to_look), "company_name"
    ].values
    filtered_companies = companies.loc[
        companies.company_name.isin(company_names), ["company_name", "company_number"]
    ]

    df_filtered = filtered_companies.set_index("company_name").join(
        psc_companies.loc[
            psc_companies.idx_company.isin(indices_to_look),
            ["idx_company", "company_name"],
        ].set_index("company_name")
    )

    return df_filtered


def get_dict_from_attr_for_companies(
    attr: str,
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
    company_number: str = "company_number",
) -> dict:
    """General function to return attribute dictionary for companies."""

    df1 = psc_companies.copy().set_index("idx_company_2")[[company_number]]
    df2 = merged_firstlink.copy().set_index("idx_company")[[company_number]]

    df1.index = df1.index.astype(int)
    df2.index = df2.index.astype(int)

    df_attr = pd.concat([df1, df2])
    df_attr = df_attr.drop_duplicates()

    df_filtered = get_company_numbers(psc_companies, df_attr, companies)
    df_filtered = df_filtered.set_index("idx_company")[[company_number]]
    df_filtered.index = df_filtered.index.astype(int)

    df_attr = pd.concat([df_attr, df_filtered]).drop_duplicates()

    companies_attr = companies[[company_number, attr]].set_index(company_number)
    df_attr = df_attr.reset_index().set_index(company_number).join(companies_attr)
    df_attr = df_attr.set_index("index")

    set_nodes = set(sorted(list(graph.nodes())))
    set_index = set(df_attr.index.values)

    indices_non_appearing = list(set_index.symmetric_difference(set_nodes))

    df_non = pd.DataFrame(index=indices_non_appearing)
    df_non[attr] = np.nan

    df_final = pd.concat([df_attr, df_non])
    attr_dict = df_final.to_dict()[attr]

    return attr_dict


def attr_kind(
    graph: nx.DiGraph, merged_firstlink: pd.DataFrame, psc_companies: pd.DataFrame
) -> dict:
    """Returns a dictionary with the psc's kind.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "kind"
    if attr in psc_companies.columns and attr in merged_firstlink.columns:
        df1 = psc_companies.set_index("idx_company")[[attr]]
        df2 = merged_firstlink.set_index("idx_company")[[attr]]

        df1.index = df1.index.astype(int)
        df2.index = df2.index.astype(int)

        df_attr = pd.concat([df1, df2])

        set_nodes = set(sorted(list(graph.nodes())))
        set_index = set(df_attr.index.values)

        indices_non_appearing = list(set_index.symmetric_difference(set_nodes))

        df_non = pd.DataFrame(index=indices_non_appearing)
        df_non[attr] = np.nan

        df_final = pd.concat([df_attr, df_non])

        attr_dict = df_final.to_dict()[attr]
        return attr_dict
    return {}


# Attribute dictionaries
def attr_human(graph: nx.DiGraph, merged_firstlink: pd.DataFrame) -> dict:
    """Returns a dictionary which answers the question 'is the node a human?'.
    The dictionary is expected to be passed to nx.set_node_attributes()"""

    human_nodes = merged_firstlink.idx_human.astype(int).unique()
    human_df = pd.DataFrame(index=sorted(list(graph.nodes())))
    human_df["human"] = False
    human_df.loc[human_nodes, "human"] = True
    human_dict = human_df.to_dict()["human"]

    return human_dict


def attr_leaf(
    graph: nx.DiGraph, merged_firstlink: pd.DataFrame, psc_companies: pd.DataFrame
) -> dict:
    """Returns a dictionary which answers the question 'is the node a leaf?'.
    The dictionary is expected to be passed to nx.set_node_attributes()"""

    owned_nodes_by_humans = merged_firstlink.idx_company.astype(int).unique()
    owners = psc_companies.idx_company.astype(int).unique()
    owned_nodes_by_companies = psc_companies.idx_company_2.astype(int).unique()

    leafs1 = [node for node in owned_nodes_by_humans if node not in owners]
    leafs2 = [node for node in owned_nodes_by_companies if node not in owners]
    leafs = leafs1 + leafs2

    leaf_df = pd.DataFrame(index=sorted(list(graph.nodes())))
    leaf_df["leaf"] = False
    leaf_df.loc[leafs, "leaf"] = True
    leaf_dict = leaf_df.to_dict()["leaf"]

    return leaf_dict


def attr_name(
    graph: nx.DiGraph, merged_firstlink: pd.DataFrame, psc_companies: pd.DataFrame
) -> dict:
    """Returns a dictionary with the nodes' names.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "name"
    attr2 = "company_name"

    df1 = psc_companies.set_index("idx_company")[[attr2]].rename(columns={attr2: attr})
    df2 = psc_companies.set_index("idx_company_2")[[attr2 + "_2"]].rename(
        columns={attr2 + "_2": attr}, index={"idx_company_2": "idx_company"}
    )
    df3 = merged_firstlink.set_index("idx_company")[[attr2]].rename(columns={attr2: attr})
    df4 = merged_firstlink.set_index("idx_human")[[attr]].rename(
        index={"idx_company_2": "idx_company"}
    )

    list_dfs = [df1, df2, df3, df4]

    for df in list_dfs:
        df.index = df.index.astype(int)

    df_attr = pd.concat(list_dfs)
    df_attr = df_attr.drop_duplicates()

    set_nodes = set(sorted(list(graph.nodes())))
    set_index = set(df_attr.index.values)

    indices_non_appearing = list(set_index.symmetric_difference(set_nodes))

    df_non = pd.DataFrame(index=indices_non_appearing)
    df_non[attr] = np.nan

    df_final = pd.concat([df_attr, df_non])

    attr_dict = df_final.to_dict()[attr]
    return attr_dict


def attr_company_numbers(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> dict:
    """Returns a dictionary with the company numbers of the company nodes.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "company_number"
    df1 = psc_companies.set_index("idx_company_2")[[attr]].rename(
        index={"idx_company_2": "idx_company"}
    )
    df2 = merged_firstlink.set_index("idx_company")[[attr]]

    df1.index = df1.index.astype(int)
    df2.index = df2.index.astype(int)

    df_attr = pd.concat([df1, df2])
    df_attr = df_attr.drop_duplicates()

    df_filtered = get_company_numbers(psc_companies, df_attr, companies)
    df_attr = pd.concat([df_attr, df_filtered.set_index("idx_company")["company_number"]])

    set_nodes = set(sorted(list(graph.nodes())))
    set_index = set(df_attr.index.values)

    indices_non_appearing = list(set_index.symmetric_difference(set_nodes))

    df_non = pd.DataFrame(index=indices_non_appearing)
    df_non[attr] = np.nan

    df_final = pd.concat([df_attr, df_non])

    attr_dict = df_final.to_dict()[attr]

    return attr_dict


def attr_previous_names(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> dict:
    """Returns a dictionary with the companies' previous names.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "previous_company_names"
    attr_dict = get_dict_from_attr_for_companies(
        attr, graph, merged_firstlink, psc_companies, companies
    )

    return attr_dict


def attr_type(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> dict:
    """Returns a dictionary with the companies' kind.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "type"
    attr_dict = get_dict_from_attr_for_companies(
        attr, graph, merged_firstlink, psc_companies, companies
    )

    return attr_dict


def attr_date_of_creation(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> dict:
    """Returns a dictionary with the company numbers of the company nodes.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "date_of_creation"
    attr_dict = get_dict_from_attr_for_companies(
        attr, graph, merged_firstlink, psc_companies, companies
    )

    return attr_dict


def attr_sic_codes(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> dict:
    """Returns a dictionary with the SIC codes of the company nodes.
    The dictionary is expected to be passed to nx.set_node_attributes()"""
    attr = "sic_codes"
    attr_dict = get_dict_from_attr_for_companies(
        attr, graph, merged_firstlink, psc_companies, companies
    )

    return attr_dict


def attr_address(
    graph: nx.DiGraph,
    merged_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
    companies: pd.DataFrame,
) -> tuple:
    """Returns two dictionaries with the addresses of nodes.
    One for the registered country and another for the registered postal code.
    The dictionary is expected to be passed to nx.set_node_attributes()"""

    psc_country = "address.country"
    psc_postal_code = "address.postal_code"

    companies_country = "registered_office_address.country"
    companies_postal_code = "registered_office_address.postal_code"

    address_psc_companies = (
        psc_companies[["idx_company", psc_country, psc_postal_code]]
        .copy()
        .rename(columns={"idx_company": "i"})
    )
    address_psc_humans = (
        merged_firstlink[["idx_human", psc_country, psc_postal_code]]
        .copy()
        .rename(columns={"idx_human": "i"})
    )

    address_pscs = pd.concat([address_psc_companies, address_psc_humans]).drop_duplicates()

    address_pscs = address_pscs.set_index("i")
    address_pscs.index = address_pscs.index.astype(int)
    address_pscs = address_pscs.rename(
        columns={psc_country: "country", psc_postal_code: "postal_code"}
    )

    j_psc_companies = psc_companies.idx_company_2.values.astype(int)
    j_psc_humans = merged_firstlink.idx_company.values.astype(int)

    js = np.unique(np.concatenate([j_psc_humans, j_psc_companies]))
    js_not_indexed = [j for j in js if j not in address_pscs.index]

    companies_not_indexed1 = psc_companies.loc[
        psc_companies.idx_company_2.isin(js_not_indexed),
        ["idx_company_2", "company_number"],
    ].rename(columns={"idx_company_2": "i"})

    companies_not_indexed2 = merged_firstlink.loc[
        merged_firstlink.idx_company.isin(js_not_indexed),
        ["idx_company", "company_number"],
    ].rename(columns={"idx_company": "i"})

    companies_not_indexed = pd.concat([companies_not_indexed1, companies_not_indexed2]).set_index(
        "company_number"
    )

    companies_not_indexed = companies_not_indexed.join(companies.set_index("company_number"))[
        ["i", companies_country, companies_postal_code]
    ].set_index("i")

    companies_not_indexed.index = companies_not_indexed.index.astype(int)

    address_companies = companies_not_indexed.rename(
        columns={companies_country: "country", companies_postal_code: "postal_code"}
    )

    addresses = pd.concat([address_pscs, address_companies])

    set_nodes = set(sorted(list(graph.nodes())))
    set_index = set(addresses.index.unique())

    indices_non_appearing = list(set_index.symmetric_difference(set_nodes))

    df_non = pd.DataFrame(index=indices_non_appearing)
    df_non["country"] = np.nan
    df_non["postal_code"] = np.nan

    addresses = pd.concat([addresses, df_non])

    df_country = addresses[["country"]]
    df_postal_code = addresses[["postal_code"]]

    dict_country = {}
    for node in df_country.index.unique():
        country = df_country.loc[node, "country"]
        if isinstance(country, pd.Series):
            list_countries = country.unique()
            if len(list_countries) == 1 and not isinstance(list_countries[0], str):
                dict_country[node] = [np.nan]
            elif len(list_countries) == 1 and isinstance(list_countries[0], str):
                dict_country[node] = [list_countries[0]]
            elif len(list_countries) > 1:
                list_ = [country for country in list_countries if isinstance(country, str)]
                dict_country[node] = list_

        else:
            dict_country[node] = [country]

    dict_postal_code = {}
    for node in df_postal_code.index.unique():
        postal_code = df_postal_code.loc[node, "postal_code"]
        if isinstance(postal_code, pd.Series):
            list_poscal_codes = postal_code.unique()
            if len(list_poscal_codes) == 1 and not isinstance(list_poscal_codes[0], str):
                dict_country[node] = [np.nan]
            elif len(list_poscal_codes) == 1 and isinstance(list_poscal_codes[0], str):
                dict_country[node] = [list_countries[0]]
            elif len(list_countries) > 1:
                list_ = [pc for pc in list_poscal_codes if isinstance(pc, str)]
                dict_country[node] = list_

        else:
            dict_postal_code[node] = [postal_code]

    return dict_country, dict_postal_code


def get_nature_of_ownership_dict(
    merged_firstlink: pd.DataFrame, psc_companies: pd.DataFrame
) -> dict:
    """Returns a dictionary with the natures of ownership list for each edge.
    The dictionary is expected to be passed to nx.set_edge_attributes()"""

    edge = "edge"
    weight = "ownership"

    df1 = psc_companies[["natures_of_control", "idx_company", "idx_company_2"]].copy()
    df2 = merged_firstlink[["natures_of_control", "idx_human", "idx_company"]].copy()

    df1[weight] = df1.natures_of_control.apply(lambda x: [n for n in x if n in types_of_ownership])
    df2[weight] = df2.natures_of_control.apply(lambda x: [n for n in x if n in types_of_ownership])

    df1[edge] = df1.apply(lambda row: (int(row["idx_company"]), int(row["idx_company_2"])), axis=1)
    df2[edge] = df2.apply(lambda row: (int(row["idx_human"]), int(row["idx_company"])), axis=1)

    df_weight = (
        pd.concat([df1[[edge, weight]], df2[[edge, weight]]]).drop_duplicates(edge).set_index(edge)
    )

    weight_dict = df_weight.to_dict()[weight]

    return weight_dict


def get_weight_dict(graph: nx.DiGraph) -> dict:
    """Function to get the weight dictionary"""
    dict_weigths_translate = {
        "more-than-25": 0.25,
        "25-to-50": 0.25,
        "50-to-75": 0.5,
        "75-to-100": 0.75,
    }

    dict_weights = {}
    edges = list(graph.edges(data=True))

    for edge in edges:
        edge_tuple = (edge[0], edge[1])
        list_ownership = edge[2]["ownership"]
        len_list = len(list_ownership)
        if len_list == 0:
            dict_weights[edge_tuple] = np.nan
        elif len_list == 1:
            value = [v for (k, v) in dict_weigths_translate.items() if k in list_ownership[0]][0]
            dict_weights[edge_tuple] = value
        else:
            values = list()
            for element in list_ownership:
                value = [v for (k, v) in dict_weigths_translate.items() if k in element][0]
                values.append(value)

            unique = np.unique(values)
            if len(unique) == 1:
                dict_weights[edge_tuple] = unique[0]
            else:
                dict_weights[edge_tuple] = np.nan

    return dict_weights
