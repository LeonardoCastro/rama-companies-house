import pandas as pd

from rama.src.rama.processing.helper_functions import fill_company_number


def clean_psc(arr_psc, string_ownership="ownership-of-shares"):
    """Function to clean PSC pd.DataFrame ad hoc.
    In the future might be changed according to the CSV file."""

    psc = pd.concat(arr_psc).reset_index(drop=True)
    psc = psc.drop(columns=["Unnamed: 0.1", "Unnamed: 0"])
    psc.natures_of_control.fillna("", inplace=True)
    psc = psc[psc.natures_of_control.str.contains(string_ownership)]
    psc.loc[:, "name"] = psc.name.str.lower().str.replace("ltd", "limited", regex=True).str.strip()
    psc.company_number = psc.company_number.apply(fill_company_number)

    return psc


def clean_companies(arr_companies):
    """Function to clean the companies pd.DataFrame ad hoc.
    In the future might be changed according to the CSV file."""
    companies = pd.concat(arr_companies).drop(columns=["Unnamed: 0"]).reset_index(drop=True)

    companies.company_number = companies.company_number.astype(str).apply(fill_company_number)
    companies.loc[:, "company_name"] = (
        companies.company_name.str.lower().str.replace("ltd", "limited", regex=True).str.strip()
    )

    return companies
