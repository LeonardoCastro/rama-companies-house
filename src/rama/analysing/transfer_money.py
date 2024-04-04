import networkx as nx
import numpy as np

dictionary_taxes = dict(
    zip(
        [
            "basic_rate",
            "higher_rate",
            "additional_rate",
            "corporation_tax",
            "personal_dividend_allowance",
        ],
        [0.0875, 0.3375, 0.3935, 0.19, 0.0],
    )
)


def loss_function(graph, initial_profits):
    """Loss function comparing the total lost wealth given a profit profile"""
    final_profits = theoretical_wrapper(graph, initial_profits)

    initial_wealth = sum(wealth for _, wealth in initial_profits.items())
    final_wealth = sum(wealth for _, wealth in final_profits.items())

    return abs(initial_wealth - final_wealth) / initial_wealth


def compose_function(func, exponent, value, **kwargs):
    """Function to compose a second function"""
    if exponent == 0:
        return 1

    output = value
    for _ in range(exponent):
        output = func(output, **kwargs)
    return output


def taxes(profit, human=True, rate="additional_rate"):
    """Function to pay taxes"""
    if human:
        if profit > dictionary_taxes["personal_dividend_allowance"]:
            cash = dictionary_taxes["personal_dividend_allowance"]
            cash += (profit - dictionary_taxes["personal_dividend_allowance"]) * (
                1 - dictionary_taxes[rate]
            )
        else:
            cash = profit
    else:
        cash = profit * (1 - dictionary_taxes["corporation_tax"])
    return cash


def get_dividend_from_neighbours(graph, node, profits):
    """Obtain dividends from downstream nodes"""
    out_hood = list(graph.neighbors(node))
    wealth = profits[node]

    if len(out_hood) != 0:
        for neighbour in out_hood:
            wealth_neighbour = get_dividend_from_neighbours(graph, neighbour, profits)
            wealth_neighbour *= graph.edges[(node, neighbour)]["weight"]
            wealth += wealth_neighbour

    return taxes(wealth, human=graph.nodes[node]["human"])


def give_dividends(graph, node, profits):
    """Take out dividends from nodes"""
    in_hood = list(graph.reverse().neighbors(node))

    wealth = profits[node]

    if len(in_hood) != 0:
        in_weights = sum(
            graph.edges[(neighbour, node)]["weight"] for neighbour in in_hood
        )
    else:
        in_weights = 0

    return (1 - in_weights) * wealth


def recursive_wrapper(graph, profits):
    """Recursive wrapper"""
    dummy_dict = {
        node: get_dividend_from_neighbours(graph, node, profits)
        for node in graph.nodes()
    }
    return_dict = {
        node: give_dividends(graph, node, dummy_dict) for node in graph.nodes()
    }
    return return_dict


def theoretical_wealth(graph, node, profits):
    """Function to get the final theoretical wealth of a node"""
    wealth = profits[node]

    for node2 in list(nx.descendants(graph, node)):
        path = nx.shortest_path(graph, node, node2)
        local_wealth = compose_function(
            taxes, len(path) - 1, profits[node2], human=False
        )
        for i in range(len(path) - 1):
            local_wealth *= graph.edges[(path[i], path[i + 1])]["weight"]
        wealth += local_wealth

    in_hood = list(graph.predecessors(node))
    in_weights = sum(graph.edges[(neighbour, node)]["weight"] for neighbour in in_hood)

    return (1 - in_weights) * taxes(wealth, human=graph.nodes[node]["human"])


def theoretical_wrapper(graph, profits):
    """Theoretical wrapper"""
    return_dict = {
        node: theoretical_wealth(graph, node, profits) for node in graph.nodes()
    }
    return return_dict
