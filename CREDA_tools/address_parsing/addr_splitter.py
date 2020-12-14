# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 05:03:14 2020

@author: fisherd
"""

import re
import pandas as pd

def split_df_addresses(addr_df: pd.DataFrame):
    '''


    Parameters
    ----------
    addr_df : pd.DataFrame
        This is a DataFrame containing your list of addresses. Specifically, this
        needs to have two columns, 'TempID' and 'parsed_Addr'. TempID contains the
        unique ID for the address entry, and parsed_Addr contains the parsed output
        from the address parser

    Returns
    -------
    return_df : pd.DataFrame
        This returns all of the addresses provided as input, but multiple addresses
        and ranges have been separated into different lines. For instance, address
        "1-9 west street" will be converted into 5 lines, "1 west street", "3 west
        street", ..., "9 west street". Each of these will have a column with their
        original TempID, but also now have a TempIDZ which is unique to each line.

    '''
    temp_idz = 0
    return_list = []
    for idx, row in addr_df.iterrows():
        addresses = row.parsed_addr
        if len(addresses) == 0:
            temp_idz = temp_idz+1
            return_list.append({'TempID':row.TempID, 'TempIDZ':temp_idz,
                                    'single_address':""})
        for address in addresses:
            if re.match('\\d+-\\d+.+', address) is not None:
                start = re.search('(\\d+)-(\\d+)', address).group(1)
                end = re.search('(\\d+)-(\\d+)', address).group(2)
                partial_address = re.search('(\\d+)-(\\d+) (.+)', address).group(3)
                for r_del in range(int(start), int(end)+1, 2):
                    temp_idz = temp_idz + 1
                    single_address = f'{r_del} {partial_address}'
                    return_list.append({'TempID':row.TempID, 'TempIDZ':temp_idz,
                                        'single_address':single_address})
            else:
                temp_idz = temp_idz + 1
                return_list.append({'TempID':row.TempID, 'TempIDZ':temp_idz,
                                    'single_address':address})

    
    return_df = pd.DataFrame(return_list)
    return return_df
