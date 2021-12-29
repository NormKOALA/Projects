'''
D - diameter, should be list
l - length of section, should be list
s - shape of section, should be list
d - direction of section, should be list
'''


def get_models_list(D = [5, 10],
                    l = [50, 100],
                    s = ['line', 'arc90', 'arc45'],
                    d = ['left', 'right', 'top', 'down']):
    
    import pandas as pd
    import numpy as np
    import itertools
    
    ### combinations for one section model
    one_section = pd.DataFrame(itertools.product(D, l, s, d),
                               columns = ['diameter',
                                          'first_length',
                                          'first_shape',
                                          'first_direction'
                                         ])
    
    one_section.drop(one_section.query("first_direction!='left'").index, inplace=True)
    one_section.reset_index(drop=True, inplace=True)
    
    descriptions=[]

    for i in range(len(one_section)):
        descriptions.append(str(list(one_section.iloc[i]))\
                            .translate(str.maketrans({',': '-',
                                                      "'": "",
                                                      "[": "",
                                                      "]": ""}))\
                            .replace(' ', ''))

    one_section['description']=descriptions
    
    ### combinations for two sections model
    two_section = pd.DataFrame(itertools.product(D, l, l, s, s, d, d),
                               columns = ['diameter',
                                          'first_length',
                                          'second_length',
                                          'first_shape',
                                          'second_shape',
                                          'first_direction',
                                          'second_direction'
                                         ])
    
    two_section.drop(two_section.query("first_direction!='left'").index, inplace=True)
    two_section.drop(two_section.query("second_shape=='line' & second_direction!='left'").index, inplace=True)
    two_section.reset_index(drop=True, inplace=True)
    
    descriptions=[]

    for i in range(len(two_section)):
        descriptions.append(str(list(two_section.iloc[i]))\
                            .translate(str.maketrans({',': '-',
                                                      "'": "",
                                                      "[": "",
                                                      "]": ""}))\
                            .replace(' ', ''))

    two_section['description']=descriptions
    
    ### combinations for three sections model
    three_section = pd.DataFrame(itertools.product(D, l, l, l, s, s, s, d, d, d),
                                 columns = ['diameter',
                                            'first_length',
                                            'second_length',
                                            'third_length',
                                            'first_shape',
                                            'second_shape',
                                            'third_shape',
                                            'first_direction',
                                            'second_direction',
                                            'third_direction'
                                           ])
    
    three_section.drop(three_section.query("first_direction!='left'").index, inplace=True)
    three_section.drop(three_section.query("second_shape=='line' & second_direction!='left'").index, inplace=True)
    three_section.drop(three_section.query("third_shape=='line' & third_direction!='left'").index, inplace=True)
    three_section.reset_index(drop=True, inplace=True)
    
    descriptions=[]

    for i in range(len(three_section)):
        descriptions.append(str(list(three_section.iloc[i]))\
                            .translate(str.maketrans({',': '-',
                                                      "'": "",
                                                      "[": "",
                                                      "]": ""}))\
                            .replace(' ', ''))

    three_section['description']=descriptions
    
    ### concatenation of all combinations
    models = pd.concat([three_section, two_section, one_section], sort=False, ignore_index=True)
    
    
    return models