import numpy as np
import datetime as dt

############ Paths ############


def find_all_paths(graph, x, path=None):
    """function to find all paths in a graph starting in a given node"""
    if path is None:
        path = []
    path = path + [x]
    paths = [path]
    for node in graph[x]:
        if node != x and node not in paths[-1]:
            newpaths = find_all_paths(graph, node, path)
            for newpath in newpaths:
                paths.append(newpath)
        else:
            paths.append([x, x])
    return paths


def keep_longest_path(list_paths):
    """Function to keep only the longest paths from a list of paths"""
    max_ = max([len(x) for x in list_paths])
    list_ = [x for x in list_paths if len(x) == max_]
    return list_


def get_max_length(graph, list_nodes):
    """Function to get the max length of a path in a graph"""
    lens = list()
    for node in list_nodes:
        lens += find_all_paths(graph, node)
    max_len = len(keep_longest_path(lens)[0]) - 1
    return max_len


############ Dates ############


def get_dates_with_nans(graph, list_nodes, format_date="%Y-%m-%d"):
    """Function to get the dates from an array containing nans"""
    dates_str = np.array(
        [
            (
                graph.nodes[node]["date_of_creation"]
                if isinstance(graph.nodes[node]["date_of_creation"], str)
                else "nan"
            )
            for node in list_nodes
        ]
    )
    dates_dt = [
        dt.datetime.strptime(date, format_date) if date != "nan" else np.nan for date in dates_str
    ]

    return dates_dt


def get_growingtime(dates, period=365.2425):
    """Function to get the growing time of a given array of dates."""
    dates_without_nans = [date for date in dates if isinstance(date, dt.datetime)]
    if len(dates_without_nans) != 0:
        life_dt = max(dates_without_nans) - min(dates_without_nans)
        life_years = life_dt.days / period
    else:
        life_years = np.nan

    return life_years


def get_min_max_dates(dates):
    """Function to get the min and max dates from an array"""
    dates = [date for date in dates if isinstance(date, dt.datetime)]
    if len(dates) != 0:
        max_ = max(dates)
        min_ = min(dates)
    else:
        max_ = np.nan
        min_ = np.nan
    return min_, max_


############ Branches ############


def get_detail_branches(
    graph, branches, dates_of_creation_dt, format_date="%Y-%m-%d", period=365.2425
):
    """Function to get the local details of branches into a dictionary"""
    detail_branches = dict()
    for b, branch in enumerate(branches):
        dict_local = dict()
        sprouts = [edge[1] for edge in graph.edges if branch == edge[0]]

        sprouts_dates_str = [graph.nodes[sprout]["date_of_creation"] for sprout in sprouts]
        sprouts_dates_dt = [
            dt.datetime.strptime(date, format_date) if isinstance(date, str) else np.nan
            for date in sprouts_dates_str
        ]

        branch_date_of_creation = dates_of_creation_dt[b]
        if isinstance(branch_date_of_creation, dt.datetime):
            growing_times_sprouts_dt = [
                date - branch_date_of_creation if isinstance(date, dt.datetime) else np.nan
                for date in sprouts_dates_dt
            ]
            growing_times_sprouts = [
                delta.days / period if isinstance(delta, dt.timedelta) else np.nan
                for delta in growing_times_sprouts_dt
            ]
        else:
            growing_times_sprouts = np.nan

        sic_codes = [graph.nodes[sprout]["sic_codes"] for sprout in sprouts]

        dict_local["sprouts"] = sprouts
        dict_local["sprouts_dates_of_creation"] = sprouts_dates_dt
        dict_local["growing_times_sprouts"] = growing_times_sprouts
        dict_local["sic_codes"] = sic_codes

        detail_branches[branch] = dict_local
    return detail_branches


def get_dict_branches(graph, list_nodes, period=365.2425, format_date="%Y-%m-%d"):
    """Function to get the dictionary of all branches"""
    dict_branches = dict()

    dates_subgraph = [graph.nodes[node]["date_of_creation"] for node in list_nodes]
    dates_subgraph_dt = [
        dt.datetime.strptime(date, format_date) for date in dates_subgraph if isinstance(date, str)
    ]

    branches = [
        node
        for node in list_nodes
        if graph.nodes[node]["out_degree"] > 1 and graph.nodes[node]["in_degree"] > 0
    ]
    degrees = [graph.nodes[branch]["out_degree"] for branch in branches]
    dates_of_creation_str = [graph.nodes[branch]["date_of_creation"] for branch in branches]
    dates_of_creation_dt = [
        dt.datetime.strptime(date, format_date) if isinstance(date, str) else np.nan
        for date in dates_of_creation_str
    ]

    if len(dates_subgraph_dt) != 0:
        min_date = min(dates_subgraph_dt)
        growing_times = [
            (delta - min_date).days / period if isinstance(delta, dt.datetime) else np.nan
            for delta in dates_of_creation_dt
        ]

    else:
        growing_times = np.nan

    detail_branches = get_detail_branches(graph, branches, dates_of_creation_dt)

    dict_branches["branches"] = branches
    dict_branches["degrees"] = degrees
    dict_branches["growing_times"] = growing_times
    dict_branches["detail_branches"] = detail_branches

    return dict_branches


############### Obtain dictionary ############


def get_dict_cluster(graph, list_nodes):
    """Function to get the dictionary of a subgraph"""
    in_degrees = np.array([graph.nodes[node]["in_degree"] for node in list_nodes])
    out_degrees = np.array([graph.nodes[node]["out_degree"] for node in list_nodes])
    degrees = list(zip(in_degrees, out_degrees))

    humans = sum([graph.nodes[node]["human"] for node in list_nodes])

    number_of_nodes = len(list_nodes)
    number_of_roots = len(np.where(in_degrees == 0)[0])
    number_of_branches = sum(
        [1 for (in_degree, out_degree) in degrees if in_degree != 0 and out_degree > 1]
    )
    max_length = get_max_length(graph, list_nodes)

    dates_with_nans = get_dates_with_nans(graph, list_nodes)
    min_date_of_creation, max_date_of_creation = get_min_max_dates(dates_with_nans)
    growing_time = get_growingtime(dates_with_nans)

    sic_codes = np.array([graph.nodes[node]["sic_codes"] for node in list_nodes])
    dict_branches = get_dict_branches(graph, list_nodes)

    dict_cluster = dict()
    dict_cluster["number_of_nodes"] = number_of_nodes
    dict_cluster["number_of_roots"] = number_of_roots
    dict_cluster["number_of_branches"] = number_of_branches
    dict_cluster["list_of_nodes"] = list_nodes
    dict_cluster["max_length"] = max_length
    dict_cluster["number_of_humans"] = humans
    dict_cluster["dates_of_creation"] = dates_with_nans
    dict_cluster["growing_time"] = growing_time
    dict_cluster["min_date_of_creation"] = min_date_of_creation
    dict_cluster["max_date_of_creation"] = max_date_of_creation
    dict_cluster["sic_codes"] = sic_codes
    dict_cluster["dict_branches"] = dict_branches

    return dict_cluster


############ Classification ############


def classify_cluster(dict_cluster):
    """Function to classify networks through their number of branches and roots"""
    number_of_nodes = dict_cluster["number_of_nodes"]
    number_of_roots = dict_cluster["number_of_roots"]
    number_of_branches = dict_cluster["number_of_branches"]

    classifications = ["boring", "bush", "arrow", "tree", "bug", "unclassified"]

    # boring ones
    if number_of_nodes < 3:
        classification = 0

    # bushes/sprouts
    elif number_of_nodes > 2 and number_of_roots == 1 and number_of_branches == 0:
        classification = 1

    # arrows
    elif number_of_nodes > 2 and number_of_roots > 1 and number_of_branches == 0:
        classification = 2

    # trees
    elif number_of_nodes > 2 and number_of_roots == 1 and number_of_branches > 0:
        classification = 3

    # bugs
    elif number_of_nodes > 2 and number_of_roots > 0 and number_of_branches > 0:
        classification = 4

    # unclassified
    else:
        classification = -1

    dict_cluster["class_int"] = classification
    dict_cluster["class_str"] = classifications[classification]

    return dict_cluster
