human_kinds = ['individual-person-with-significant-control',
               'individual-beneficial-owner',             
              ]

company_kinds = ['corporate-entity-person-with-significant-control',
                 'corporate-entity-beneficial-owner',
                 'legal-person-person-with-significant-control',
                ]

other_kinds = ['super-secure-person-with-significant-control']

types_of_ownership = [
    'ownership-of-shares-25-to-50-percent',
    'ownership-of-shares-25-to-50-percent-as-firm',
    'ownership-of-shares-25-to-50-percent-as-trust',
    'ownership-of-shares-50-to-75-percent',
    'ownership-of-shares-50-to-75-percent-as-firm',
    'ownership-of-shares-50-to-75-percent-as-trust',
    'ownership-of-shares-75-to-100-percent',
    'ownership-of-shares-75-to-100-percent-as-firm',
    'ownership-of-shares-75-to-100-percent-as-trust',
    'ownership-of-shares-more-than-25-percent-registered-overseas-entity',
]

psc_columns = ['natures_of_control',
               'ceased_on', 
               'name', 
               'country_of_residence',
               'kind', 
               'nationality', 
               'notified_on', 
               'date_of_birth.year',
               'date_of_birth.month', 
               'name_elements.surname', 
               'name_elements.forename',
               'name_elements.title',
               'name_elements.middle_name',
               'company_number', 
               'identification.registration_number',
               'ceased',
               'address.country',
               'address.postal_code',
              ]

psc_columns_rename = {
               'name': 'CompanyName',
               'date_of_birth.year': 'date_of_birth_year',
               'date_of_birth.month': 'date_of_birth_month', 
               'name_elements.surname': 'name_surname', 
               'name_elements.forename': 'name_forename',
               'name_elements.title': 'name_title',
               'name_elements.middle_name': 'name_middle_name',
               'identification.registration_number': 'registration_number',
}

companies_columns = ['CompanyName', 
                     'CompanyNumber', 
                     'CompanyCategory', 
                     'CompanyStatus',
                     'CountryOfOrigin', 
                     'DissolutionDate', 
                     'IncorporationDate',
                     'PreviousName_1.CONDATE',
                     'PreviousName_1.CompanyName', 
                     'PreviousName_2.CONDATE',
                     'PreviousName_2.CompanyName', 
                     'PreviousName_3.CONDATE',
                     'PreviousName_3.CompanyName', 
                     'PreviousName_4.CONDATE',
                     'PreviousName_4.CompanyName', 
                     'PreviousName_5.CONDATE',
                     'PreviousName_5.CompanyName', 
                     'PreviousName_6.CONDATE',
                     'PreviousName_6.CompanyName', 
                     'PreviousName_7.CONDATE',
                     'PreviousName_7.CompanyName', 
                     'PreviousName_8.CONDATE',
                     'PreviousName_8.CompanyName', 
                     'PreviousName_9.CONDATE',
                     'PreviousName_9.CompanyName', 
                     'PreviousName_10.CONDATE',
                     'PreviousName_10.CompanyName'
                    ]

companies_columns_rename = {
                     'PreviousName_1.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_1.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_2.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_2.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_3.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_3.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_4.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_4.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_5.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_5.CompanyName': 'PreviousName_1_CompanyName',
                     'PreviousName_6.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_6.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_7.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_7.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_8.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_8.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_9.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_9.CompanyName': 'PreviousName_1_CompanyName', 
                     'PreviousName_10.CONDATE': 'PreviousName_1_CONDATE',
                     'PreviousName_10.CompanyName': 'PreviousName_1_CompanyName', 
                    }

natures_patterns_str = [
                        'ownership-of-shares', 
                        'part-right-to-share-surplus-assets', 
                        'right-to-appoint-and-remove-directors', 
                        'right-to-appoint-and-remove-members',
                        'right-to-appoint-and-remove-person',
                        'right-to-share-surplus-assets',
                        'significant-influence-or-control',
                        'voting-rights',
                       ]

