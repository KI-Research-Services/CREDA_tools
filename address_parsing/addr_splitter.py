# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 05:03:14 2020

@author: fisherd
"""

import re
import pandas as pd

def split_df_addresses(addr_df):
    TempIDZ = 0
    return_list = []
    
    for idx, row in addr_df.iterrows():
        addresses = row.parsed_Addr
        for address in addresses:
            if re.match('\d+-\d+.+', address) is not None:
                print(address)
                start = re.search('(\d+)-(\d+)', address).group(1)
                end = re.search('(\d+)-(\d+)', address).group(2)
                partial_address = re.search('(\d+)-(\d+) (.+)', address).group(3)
                for x in range(int(start), int(end), 2):
                    TempIDZ = TempIDZ + 1
                    single_address =f'{x} {partial_address}'
                    return_list.append({'TempID':row.TempID,'TempIDZ':TempIDZ,'address':single_address})
            else:
                TempIDZ = TempIDZ + 1
                return_list.append({'TempID':row.TempID,'TempIDZ':TempIDZ,'address':address})
        
    
    return_df = pd.DataFrame(return_list)
    return return_df

