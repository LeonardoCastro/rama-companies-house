from tqdm import tqdm
import pandas as pd

def test_humans(small_firstlink):
    list_nonpass = list()
    print('Testing humans correctly indexed')
    for idx_h in tqdm(small_firstlink.idx_human.sort_values().unique()):
        if len(small_firstlink.loc[small_firstlink.idx_human==idx_h].name.unique()) != 1:
            list_nonpass.append(idx_h)
        assert len(list_nonpass) == 0
    
def test_companies_names(small_firstlink):
    list_nonpass = list()
    print('Testing Companies Names')
    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        if len(small_firstlink.loc[small_firstlink.idx_company==idx_c].company_name.unique()) != 1:
                list_nonpass.append(idx_c)
        #assert len(list_nonpass)== 0
    return list_nonpass
    
def test_compare_companies_between_df(small_firstlink, companies):
    list_nonpass = list()
    print('Comparing companies between dataframes')
    small_companies = companies.loc[companies.company_number.isin(small_firstlink.company_number.unique()), 
                                    ['company_name', 'company_number']]
    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        
        df = small_firstlink.loc[small_firstlink.idx_company==idx_c, ['company_name', 'company_number']]
        name_totry = df.company_name.values[0]
        number_totry = df.company_number.values[0]
        
        name_reference = small_companies.loc[small_companies.company_number==number_totry, 'company_name'].values[0]
        
        if name_reference != name_totry:
            list_nonpass.append(idx_c)
        assert len(list_nonpass) == 0

def test_companies_number(small_firstlink):
    list_nonpass = list()
    print('Testing Companies Numbers')
    for idx_c in tqdm(small_firstlink.idx_company.sort_values().unique()):
        if len(small_firstlink.loc[small_firstlink.idx_company==idx_c].company_number.unique()) != 1:
                list_nonpass.append(idx_c)
    return list_nonpass

def test_companies_number2(small_firstlink):
    list_nonpass = list()
    print('Testing Companies Numbers')
    for idx_c in tqdm(small_firstlink.idx_company_2.sort_values().unique()):
        if len(small_firstlink.loc[small_firstlink.idx_company_2==idx_c].company_number.unique()) != 1:
                list_nonpass.append(idx_c)
    return list_nonpass
    
def test_compare_companies_between_df2(small_firstlink, companies):
    list_nonpass = list()
    print('Comparing companies between dataframes')
    small_companies = companies.loc[companies.company_number.isin(small_firstlink.company_number.unique()), 
                                    ['company_name', 'company_number']]
    for idx_c in tqdm(small_firstlink.idx_company_2.sort_values().unique()):
        
        df = small_firstlink.loc[small_firstlink.idx_company_2==idx_c, ['company_name', 'company_number']]
        name_totry = df.company_name.values[0]
        number_totry = df.company_number.values[0]
        
        name_reference = small_companies.loc[small_companies.company_number==number_totry, 'company_name'].values[0]
        
        if name_reference != name_totry:
            list_nonpass.append(idx_c)
    assert len(list_nonpass) == 0