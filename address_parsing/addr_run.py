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
    and returns a dataframe of parsed addresses.

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
    address_lines['addr'] = address_lines['addr'].str.lower()
    address_lines['parsed_addr'] = address_lines['addr']
    address_lines['flags'] = ""
    
    parsed_addresses = parse_addr_df(address_lines, expand_addresses, outfile)
    
    return parsed_addresses
    
def parse_addr_df(address_lines: pd.DataFrame, expand_addresses: bool = True, outfile = "parsed_addrs.csv") -> pd.DataFrame:
    '''
    

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
