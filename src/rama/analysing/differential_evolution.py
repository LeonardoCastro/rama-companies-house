import random
import networkx as nx
import numpy as np
from tqdm import tqdm

from rama.src.rama.analysing.transfer_money import loss_function


def make_profit_dict(profit_distribution, nodes_with_profit, nodes_without_profit):
    """Function to make the profit dictionary"""
    dict_ = dict(zip(nodes_with_profit, profit_distribution))
    for node in nodes_without_profit:
        dict_[node] = 0
    return dict_


def _get_losses_of_generations(subgraph, population, nodes_with_profit, loss_func):
    """Function to get the array of losses for the entire population"""
    pop_size = population.shape[0]
    nodes_without_profit = [node for node in subgraph.nodes() if node not in nodes_with_profit]
    losses = []
    for pop in range(pop_size):
        wealth = population[pop]
        wealth = wealth / sum(wealth)
        dict_wealth = make_profit_dict(wealth, nodes_with_profit, nodes_without_profit)
        loss = loss_func(subgraph, dict_wealth)
        losses.append(loss)
    return losses


def _get_trial_and_target_vectors(population, differential_weight, crossover_probability):
    """Function to get a trial and target vector, part of the differential evolution algorithm"""
    pop_size, len_companies = population.shape
    sample = random.sample(range(pop_size), 4)

    target = sample[0]
    base = sample[1]
    upper = sample[2]
    lower = sample[3]

    certain_replacement = np.random.randint(0, len_companies)

    # get mutant vector
    target_vector = population[target]
    mutant_vector = population[base] + differential_weight * (population[upper] - population[lower])

    constraints = (np.around(mutant_vector, decimals=2) > 0) & (
        np.around(mutant_vector, decimals=2) < 1
    )
    mutant_vector[~constraints] = np.random.rand(sum(~constraints))

    tests = np.random.rand(len_companies) <= crossover_probability
    tests[certain_replacement] = True

    # crossover
    trial_vector = target_vector.copy()
    trial_vector[tests] = mutant_vector[tests]

    # normalization
    trial_vector = trial_vector / sum(trial_vector)
    target_vector = target_vector / sum(target_vector)

    return trial_vector, target_vector, target


def _get_next_generation_vector(
    subgraph,
    trial_vector,
    target_vector,
    nodes_with_profit,
    loss_func,
    conditions=False,
):
    """Function to get the next generation vector"""
    len_companies = len(nodes_with_profit)
    nodes_without_profit = [node for node in subgraph.nodes() if node not in nodes_with_profit]

    dict_trial = make_profit_dict(trial_vector, nodes_with_profit, nodes_without_profit)
    dict_target = make_profit_dict(target_vector, nodes_with_profit, nodes_without_profit)

    loss_trial = loss_func(subgraph, dict_trial)
    loss_target = loss_func(subgraph, dict_target)

    if conditions:
        conditions_target = sum(
            (np.around(target_vector, decimals=2) < 1) & (np.around(target_vector, decimals=2) > 0)
        )
        conditions_trial = sum(
            (np.around(trial_vector, decimals=2) < 1) & (np.around(trial_vector, decimals=2) > 0)
        )
        vector = _select_vector(
            loss_trial, loss_target, conditions_trial, conditions_target, len_companies
        )
    else:
        if loss_trial < loss_target:
            vector = "trial"
        else:
            vector = "target"

    return vector


def _select_vector(loss_trial, loss_target, conditions_trial, conditions_target, len_companies):
    vector = "target"
    # If target vector follows all constraints
    if conditions_target == len_companies:
        # If trial vector follows all constraints
        if conditions_trial == len_companies:
            # Then it is about who is better
            if loss_trial < loss_target:
                vector = "trial"
            # If target is feasible but trial is not: nothing to do

    else:
        # if target is not feable but trial is
        if conditions_trial == len_companies:
            vector = "trial"

        # if both are not feasable
        if conditions_trial != len_companies:
            if conditions_trial > conditions_target and loss_trial < loss_target:
                vector = "trial"
    return vector


def differential_evolution(
    subgraph,
    differential_weight,
    crossover_probability,
    generations,
    max_iterations,
    loss_func=loss_function,
    disable_tqdm=False,
):
    """General function to run a differential evolution algorithm"""
    # initiate income
    # list_of_nodes = list(subgraph.nodes)
    # dict_incomes = dict(zip(list_of_nodes, np.zeros(len(list_of_nodes))))

    # nx.set_node_attributes(subgraph, dict_incomes, "income")

    nodes_with_profit = [node for node in subgraph.nodes() if not subgraph.nodes[node]["human"]]

    # initiate DE
    len_companies = len(nodes_with_profit)
    pop_size = generations * len_companies

    population = np.random.rand(pop_size, len_companies)
    for pop in range(pop_size):
        population[pop] = population[pop] / sum(population[pop])

    bests = []
    for _ in tqdm(range(max_iterations), disable=disable_tqdm):
        trial_vector, target_vector, target = _get_trial_and_target_vectors(
            population, differential_weight, crossover_probability
        )

        vector = _get_next_generation_vector(
            subgraph, trial_vector, target_vector, nodes_with_profit, loss_func
        )

        if vector == "trial":
            population[target] = trial_vector

        losses = _get_losses_of_generations(subgraph, population, nodes_with_profit, loss_func)
        bests.append(min(losses))

    losses = _get_losses_of_generations(subgraph, population, nodes_with_profit, loss_func)

    idx = np.where(np.array(losses) == min(losses))[0]
    best_distribution = population[idx]

    return best_distribution, bests
