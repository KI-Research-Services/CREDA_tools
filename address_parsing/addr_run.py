# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 21:53:53 2020

@author: fisherd
"""

import pandas as pd

# my libraries
from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter

def parse_addr_file(address_file: str, expand_addresses: bool = True, outfile = "parsed_addrs.csv") -> pd.DataFrame:
    '''
    This takes a single filename, with a specific format for required columns,
    and returns a dataframe of parsed addresses. Most of the work is done by the
    parse_addr_df function, but this function cleans up input and creates extra
    columns needed.

    Parameters
    ----------
    address_file : str
        Relative address to infile for addresses. This MUST contain a column called
        'addr', which is the street address (no city/state) of the property
    expand_addresses : bool, optional
        Boolean value that expresses whether to do a final expansion on the output,
        as in switch ranges to multiple lines. The default is True.
    outfile : TYPE, optional
        The outfile to which to save address results. The default is "parsed_addrs.csv",
        and it will go in the output folder.

    Returns
    -------
    None.

    '''
    address_lines = pd.read_csv(address_file)
    address_lines.reset_index(inplace=True)
    address_lines.rename(columns={'index':'TempID'}, inplace=True)
    address_lines['TempID'] = address_lines['TempID'] + 1
    try:
        address_lines['addr'] = address_lines['addr'].str.lower()
    except KeyError:
        print("\n***ERROR***\n-Invalid input format. Infile must have address columns 'addr'.")
        print(address_lines.columns)
        return None
    address_lines['parsed_addr'] = address_lines['addr']
    address_lines['flags'] = ""
    
    parsed_addresses = parse_addr_df(address_lines, expand_addresses, outfile)
    
    return parsed_addresses
    
def parse_addr_df(address_lines: pd.DataFrame, expand_addresses: bool = True, outfile = "parsed_addrs.csv") -> pd.DataFrame:
    '''
    This takes a single filename, with a specific format for required columns,
    and returns a dataframe of parsed addresses. The input addresses should be
    in all lower case by this point, and there should be 3 specific columns in
    the dataframe - addr, parsed_addr (currently empty), and flags (currently
    empty)

    Parameters
    ----------
    address_lines : pd.DataFrame
        DESCRIPTION.
    expand_addresses : bool, optional
        DESCRIPTION. The default is True.
    outfile : TYPE, optional
        DESCRIPTION. The default is "parsed_addrs.csv".

    Returns
    -------
    None.

    '''
        
    for idx, row in address_lines.copy().iterrows():
        temp = algo_grammar.AddrParser(row['addr'])
        row['parsed_addr'] = temp.get_addrs()
        row['flags'] = temp.get_flags()
        address_lines.iloc[idx] = row

    if expand_addresses:
        temp = addr_splitter.split_df_addresses(address_lines[['TempID', 'parsed_addr']])
        address_lines = pd.merge(address_lines, temp, how='inner', on='TempID')
    else:
        address_lines.TempIDZ = address_lines.TempID
        
    outfile = f'addresses_out\\{outfile}'
    address_lines = address_lines[['TempID','TempIDZ','addr','single_address', 'city', 'state', 'zip', 'parsed_addr', 'flags']]
    address_lines[['TempID', 'TempIDZ','addr','single_address','city','state','zip']].to_csv(outfile, index=False)
    print(f'\nAddress parsing now completed and saved to addresses_out\\{outfile}')
    print(f'Please geocode using "single_address" and "TempIDZ" fields and place results in "geocoded_in" folder')
    
    return address_lines