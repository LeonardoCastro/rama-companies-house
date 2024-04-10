"""Pytest configuration file."""

import pandas as pd
import pytest


@pytest.fixture(scope="function")
def init_first_link():
    """Returns a simple pandas DataFrame like the one processed by Rama"""
    first_link = pd.DataFrame(
        data={
            "name": ["Alice", "Bob", "Charles", "Dave", "Emma", "Frances"],
            "company_name": ["Ecila", "bob", "Selrahc", "Evade", "Ammerica", "Secnarfff"],
            "company_number": ["1234", "5678", "9012", "3456", "7890"],
            "idx_human": [1, 2, 3, 4, 5],
            "idx_company": [11, 12, 13, 14, 15],
        }
    )
    return first_link
