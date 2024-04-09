from tqdm import tqdm


def test_compare_companies_between_df(small_firstlink, companies):
    "Comparing companies between dataframes"
    list_nonpass = []
    small_companies = companies.loc[
        companies.company_number.isin(small_firstlink.company_number.unique()),
        ["company_name", "company_number"],
    ]
    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        df = small_firstlink.loc[
            small_firstlink.idx_company == idx_c, ["company_name", "company_number"]
        ]
        name_totry = df.company_name.values[0]
        number_totry = df.company_number.values[0]

        name_reference = small_companies.loc[
            small_companies.company_number == number_totry, "company_name"
        ].values[0]

        if name_reference != name_totry:
            list_nonpass.append(idx_c)
        assert len(list_nonpass) == 0


def test_companies_number2(small_firstlink):
    "Testing Companies Numbers"
    list_nonpass = []
    for idx_c in tqdm(small_firstlink.idx_company_2.sort_values().unique()):
        if (
            len(small_firstlink.loc[small_firstlink.idx_company_2 == idx_c].company_number.unique())
            != 1
        ):
            list_nonpass.append(idx_c)
    return list_nonpass


def test_compare_companies_between_df2(small_firstlink, companies):
    "Comparing companies between dataframes"
    list_nonpass = []

    small_companies = companies.loc[
        companies.company_number.isin(small_firstlink.company_number.unique()),
        ["company_name", "company_number"],
    ]
    for idx_c in tqdm(small_firstlink.idx_company_2.sort_values().unique()):
        df = small_firstlink.loc[
            small_firstlink.idx_company_2 == idx_c, ["company_name", "company_number"]
        ]
        name_totry = df.company_name.values[0]
        number_totry = df.company_number.values[0]

        name_reference = small_companies.loc[
            small_companies.company_number == number_totry, "company_name"
        ].values[0]

        if name_reference != name_totry:
            list_nonpass.append(idx_c)
    assert len(list_nonpass) == 0
