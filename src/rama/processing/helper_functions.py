import os
from typing import Sequence

import numpy as np
import pandas as pd


def check_dir_exists(path: str) -> None:
    """Checks if folder directory already exists, else makes directory.
    Args:
        path (str): folder path for saving.
    """
    is_exist = os.path.exists(path)
    if not is_exist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print(f"Creating {path} folder")
    else:
        print(f"Folder exists: {path}")


def get_mutual_company_numbers(psc: pd.DataFrame, companies: pd.DataFrame) -> np.ndarray:
    """Function to match company numbers from PSCs and companies"""
    company_numbers_psc = psc.company_number.values
    if "CompanyNumber" in companies.columns:
        mutual_company_numbers = companies.loc[
            companies.CompanyNumber.isin(company_numbers_psc)
        ].CompanyNumber.values
    elif "company_number" in companies.columns:
        mutual_company_numbers = companies.loc[
            companies.company_number.isin(company_numbers_psc)
        ].company_number.values

    return mutual_company_numbers


def fill_company_number(x: str, max_length: int = 8) -> str:
    """Function to fill the company number with 0s to get a uniform format for them"""
    missing_length = max_length - len(x)

    if missing_length == 0:
        complete_number = x
    else:
        complete_number = missing_length * "0" + x

    return complete_number


def get_human_company_links(
    psc: pd.DataFrame,
    companies: pd.DataFrame,
    mutual_company_numbers: Sequence[str],
    psc_columns: list,
    human_kinds: list,
    companies_columns: list,
) -> pd.DataFrame:
    """Function to link a human PSC with a company they own/control"""
    psc_humans = psc[psc_columns]
    psc_humans = psc_humans.loc[
        (psc.company_number.isin(mutual_company_numbers)) & (psc.kind.isin(human_kinds))
    ].reset_index(drop=True)
    duplicated_humans = psc_humans.duplicated(
        subset=["name", "date_of_birth.year", "date_of_birth.month"]
    )
    all_duplicated_humans = psc_humans.duplicated(
        subset=["name", "date_of_birth.year", "date_of_birth.month"], keep=False
    )
    humans_bool = np.logical_or(duplicated_humans, ~all_duplicated_humans)

    idx_humans = [int(i) + 1 for i in range(sum(humans_bool))]
    psc_humans.loc[humans_bool, ["idx_human"]] = idx_humans

    psc_humans["idx_human"].fillna(
        psc_humans.groupby(["name", "date_of_birth.year", "date_of_birth.month"])[
            "idx_human"
        ].transform("first"),
        inplace=True,
    )

    if "CompanyNumber" in companies.columns:
        companies_mutual = companies.loc[
            (companies.CompanyNumber.isin(mutual_company_numbers)), companies_columns
        ]
        companies_mutual = companies_mutual.rename(columns={"CompanyNumber": "company_number"})
    else:
        companies_mutual = companies.loc[(companies.company_number.isin(mutual_company_numbers)), :]

    duplicated_companies = companies_mutual.duplicated(subset="company_number")
    all_duplicated_companies = companies_mutual.duplicated(subset="company_number", keep=False)

    companies_bool = np.logical_or(duplicated_companies, ~all_duplicated_companies)

    idx_companies = [
        int(i) + 1 for i in range(len(idx_humans), len(idx_humans) + sum(companies_bool))
    ]
    companies_mutual.loc[companies_bool, ["idx_company"]] = idx_companies

    companies_mutual["idx_company"].fillna(
        companies_mutual.groupby("company_number")["idx_company"].transform("first"), inplace=True
    )

    merged_firstlink = (
        psc_humans.set_index("company_number")
        .join(companies_mutual.set_index("company_number"))
        .reset_index()
    )

    return merged_firstlink


def get_company_company_link(
    psc: pd.DataFrame, companies: pd.DataFrame, small_firstlink: pd.DataFrame, company_kinds: list
) -> pd.DataFrame:
    """Function to link a company PSC with another company it owns/controls"""

    psc_companies = psc.loc[(psc.kind.isin(company_kinds))].reset_index(drop=True)

    # psc_companies.loc[:, 'name'] = psc.name.str.lower()
    psc_companies = psc_companies.rename(columns={"name": "company_name"})
    psc_companies = psc_companies.dropna(subset=["company_name"])

    # Fill owned companies that have already been indexed as owners of other companies
    if "company_number" not in companies.columns:
        companies = companies.rename(columns={"CompanyNumber": "company_number"})
    if "company_name" not in companies.columns:
        companies = companies.rename(columns={"CompanyName": "company_name"})
    names_owned = companies.loc[
        companies.company_number.isin(psc_companies.company_number),
        ["company_number", "company_name"],
    ]

    psc_companies = (
        psc_companies.set_index("company_number")
        .join(names_owned.set_index("company_number"), rsuffix="_2")
        .reset_index()
    )

    # 1 - Index Owners already indexed
    already_indexed_owners = small_firstlink[
        small_firstlink.company_name.isin(psc_companies.company_name.unique())
    ][["company_name", "idx_company"]].drop_duplicates()

    psc_companies = (
        psc_companies.set_index("company_name")
        .join(already_indexed_owners.set_index("company_name"))
        .reset_index()
    )

    # 2 - Index Owners not seen before

    # do not take into account those that appear in company_names_2
    idxs_nan = psc_companies.idx_company.isna()
    #
    idx_leafs = psc_companies.loc[
        psc_companies.company_name.isin(psc_companies.company_name_2.values)
    ].index
    idxs_nan[idx_leafs.to_list()] = False
    #

    min_ = int(small_firstlink[["idx_human", "idx_company"]].max().max())
    max_ = min_ + len(psc_companies[idxs_nan].company_name.unique())
    idxs = [i + 1 for i in range(min_, max_)]

    duplicated_companies = psc_companies[idxs_nan].duplicated("company_name", keep="first")

    companies_bool = np.logical_and(idxs_nan, ~duplicated_companies)

    psc_companies.loc[companies_bool, ["idx_company"]] = idxs

    psc_companies["idx_company"].fillna(
        psc_companies.groupby("company_name")["idx_company"].transform("first"), inplace=True
    )

    # Second companies
    # 1 - Index Owneds already indexed by company number
    already_indexed_owneds_number = small_firstlink[
        small_firstlink.company_number.isin(psc_companies.company_number.unique())
    ][["company_number", "idx_company"]].drop_duplicates()

    # Fill owned companies that have already been indexed in the first step human-company link
    psc_companies = (
        psc_companies.set_index("company_number")
        .join(already_indexed_owneds_number.set_index("company_number"), rsuffix="_2")
        .reset_index()
    )

    # 2 - Index Owneds already indexed in column 1 by name
    # Fill owned companies that have already been indexed as owners of other companies
    unique_names_owned = names_owned.company_name.unique()
    min_ = max_
    max_ = min_ + len(unique_names_owned)
    idxs = [i + 1 for i in range(min_, max_)]

    for idx, name in enumerate(unique_names_owned):
        psc_companies.loc[psc_companies.company_name == name, "idx_company"] = idxs[idx]
        psc_companies.loc[psc_companies.company_name_2 == name, "idx_company_2"] = idxs[idx]

    # Detect those owned companies that have been indexed as owners
    idxs_nan = psc_companies.idx_company_2.isna()
    min_ = int(psc_companies["idx_company"].max())
    max_ = min_ + len(psc_companies[idxs_nan].company_number.unique())
    idxs = [i + 1 for i in range(min_, max_)]

    duplicated_companies = psc_companies[idxs_nan].duplicated("company_number", keep="first")

    companies_bool = np.logical_and(idxs_nan, ~duplicated_companies)

    psc_companies.loc[companies_bool, ["idx_company_2"]] = idxs

    psc_companies["idx_company_2"].fillna(
        psc_companies.groupby("company_number")["idx_company_2"].transform("first"), inplace=True
    )

    return psc_companies


def get_list_unique_natures_of_control(psc: pd.DataFrame) -> list:
    """Function to get a list of the unique natures of control strings"""
    psc.natures_of_control.fillna("", inplace=True)
    natures = psc.natures_of_control.unique()

    list_unique_natures = []
    for _, list_str in enumerate(natures):
        if list_str != "":
            eval_list = eval(list_str)
            for element in eval_list:
                list_unique_natures.append(element)

    list_unique_natures = np.unique(np.array(list_unique_natures))

    return list_unique_natures
