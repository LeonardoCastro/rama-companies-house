from typing import Sequence
import numpy as np
import pandas as pd
import networkx as nx

from rama.src.rama.processing.helper_functions import (
    get_mutual_company_numbers,
    get_human_company_links,
    get_company_company_link,
)
from rama.src.rama.processing.lists import (
    psc_columns,
    human_kinds,
    companies_columns,
    company_kinds,
    other_kinds,
)
from rama.src.rama.processing.cleaning import clean_psc, clean_companies


def process_database(
    arr_psc: Sequence[pd.DataFrame],
    arr_companies: Sequence[pd.DataFrame],
    string_ownership: str = "ownership-of-shares",
) -> tuple:
    """Function that processes the database and returns the dataframes and the edgelist."""
    psc = clean_psc(arr_psc, string_ownership)
    companies = clean_companies(arr_companies)

    merged_firstlink, small_firstlink = get_firstlink(psc, companies)
    psc_companies = get_secondlink(psc, companies, small_firstlink)
    sspsc = get_sspsc(psc, companies, small_firstlink, psc_companies)

    list_dfs = [companies, merged_firstlink, psc_companies, sspsc]

    edge_list = get_edge_list(small_firstlink, psc_companies, sspsc)

    return list_dfs, edge_list


def get_firstlink(
    psc: pd.DataFrame,
    companies: pd.DataFrame,
) -> tuple:
    """Function that returns both DataFrames containing the firstlink"""

    mutual_company_numbers = get_mutual_company_numbers(psc, companies)

    merged_firstlink = get_human_company_links(
        psc,
        companies,
        mutual_company_numbers,
        psc_columns,
        human_kinds,
        companies_columns,
    )
    merged_firstlink.natures_of_control = merged_firstlink.natures_of_control.apply(
        lambda x: x.split("'")[1::2]
    )

    small_firstlink = merged_firstlink[
        ["name", "company_name", "company_number", "idx_human", "idx_company"]
    ].copy()
    small_firstlink.loc[:, "company_name"] = small_firstlink.company_name.str.lower()

    return merged_firstlink, small_firstlink


def get_secondlink(
    psc: pd.DataFrame, companies: pd.DataFrame, small_firstlink: pd.DataFrame
) -> pd.DataFrame:
    """Return DataFrame containing second links"""
    psc_companies = get_company_company_link(psc, companies, small_firstlink, company_kinds)
    psc_companies.natures_of_control = psc_companies.natures_of_control.apply(
        lambda x: x.split("'")[1::2]
    )

    return psc_companies


def get_sspsc(
    psc: pd.DataFrame,
    companies: pd.DataFrame,
    small_firstlink: pd.DataFrame,
    psc_companies: pd.DataFrame,
) -> pd.DataFrame:
    """Function to get links coming from SSPSCs"""
    sspsc = psc.loc[psc.kind.isin(other_kinds)].copy()
    company_numbers_sspsc = sspsc.company_number.unique()

    df_names = companies.loc[
        companies.company_number.isin(company_numbers_sspsc),
        ["company_number", "company_name"],
    ]
    company_names_sspsc = df_names.company_name.unique()

    sspsc = (
        sspsc.set_index("company_number").join(df_names.set_index("company_number")).reset_index()
    )

    min_ = int(psc_companies["idx_company_2"].max())
    max_ = min_ + len(sspsc)
    idxs = [i + 1 for i in range(min_, max_)]

    sspsc.loc[:, "i"] = idxs

    a = small_firstlink.loc[small_firstlink.company_number.isin(company_numbers_sspsc)]
    b = psc_companies.loc[psc_companies.company_number.isin(company_numbers_sspsc)]
    c = psc_companies.loc[psc_companies.company_name.isin(company_names_sspsc)]
    d = psc_companies.loc[psc_companies.company_name_2.isin(company_names_sspsc)]

    for df in [a, b]:
        if len(df) > 0:
            sspsc = (
                sspsc.set_index("company_number")
                .join(df.set_index("company_number")["idx_company"].drop_duplicates())
                .reset_index()
            )

    for df in [c, d]:
        if len(df) > 0:
            sspsc = (
                sspsc.set_index("company_name")
                .join(df.set_index("company_name")["idx_company"].drop_duplicates())
                .reset_index()
            )

    if "idx_company" not in sspsc.columns:
        sspsc["idx_company"] = np.nan

    duplicated_companies = sspsc.loc[sspsc.idx_company.isna(), :].duplicated(
        subset="company_number"
    )
    all_duplicated_companies = sspsc.loc[sspsc.idx_company.isna(), :].duplicated(
        subset="company_number", keep=False
    )

    companies_bool = np.logical_or(duplicated_companies, ~all_duplicated_companies)

    s = sspsc.loc[~sspsc.idx_company.isna(), :].idx_company.isna()
    companies_bool = pd.concat([companies_bool, s]).sort_index()

    idx_nan = sspsc.drop_duplicates("company_number").idx_company.isna()

    min_ = max_
    max_ = min_ + sum(idx_nan)
    idxs = [i + 1 for i in range(min_, max_)]

    sspsc.loc[companies_bool.values, ["idx_company"]] = idxs
    sspsc["idx_company"].fillna(
        sspsc.groupby("company_number")["idx_company"].transform("first"), inplace=True
    )

    return sspsc


def get_edge_list(
    small_firstlink: pd.DataFrame, psc_companies: pd.DataFrame, sspsc: pd.DataFrame
) -> pd.DataFrame:
    """Function to get the edgelist"""
    edge_list_companies = (
        psc_companies[["idx_company", "idx_company_2"]]
        .copy()
        .rename(columns={"idx_company": "i", "idx_company_2": "j"})
        .astype(int)
    )

    edge_list_humans = (
        small_firstlink[["idx_human", "idx_company"]]
        .copy()
        .rename(columns={"idx_human": "i", "idx_company": "j"})
        .astype(int)
    )

    edge_list_sspsc = (
        sspsc[["i", "idx_company"]].copy().rename(columns={"idx_company": "j"}).astype(int)
    )

    edge_list = pd.concat(
        [
            edge_list_humans,
            edge_list_companies,
            edge_list_sspsc,
        ]
    ).reset_index()

    return edge_list


def get_graph(edge_list: pd.DataFrame) -> nx.DiGraph:
    """Function that takes the edgelist and returns a nx.DiGraph"""
    origins = [int(i) for i in edge_list.i.values]
    destinations = [int(j) for j in edge_list.j.values]
    edge_list_ints = list(zip(origins, destinations))

    graph = nx.from_edgelist(edge_list_ints, create_using=nx.DiGraph)

    return graph
