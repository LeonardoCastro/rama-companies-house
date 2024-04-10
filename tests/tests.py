"""Pytest tests"""

from tqdm import tqdm


def test_humans(init_first_link):
    "Testing humans correctly indexed"
    small_firstlink = init_first_link
    list_nonpass = []
    for idx_h in tqdm(small_firstlink.idx_human.sort_values().unique()):
        if len(small_firstlink.loc[small_firstlink.idx_human == idx_h].name.unique()) != 1:
            list_nonpass.append(idx_h)
        assert len(list_nonpass) == 0


def test_companies_names(init_first_link):
    "Testing Companies Names"
    small_firstlink = init_first_link
    list_nonpass = []

    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        if (
            len(small_firstlink.loc[small_firstlink.idx_company == idx_c].company_name.unique())
            != 1
        ):
            list_nonpass.append(idx_c)
        # assert len(list_nonpass)== 0
    return list_nonpass


def test_companies_number(init_first_link):
    "Testing Companies Numbers"
    small_firstlink = init_first_link
    list_nonpass = []

    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        if (
            len(small_firstlink.loc[small_firstlink.idx_company == idx_c].company_number.unique())
            != 1
        ):
            list_nonpass.append(idx_c)
    return list_nonpass
