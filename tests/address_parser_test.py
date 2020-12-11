# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 07:09:51 2020

@author: fisherd
"""
import numpy as np
import pandas as pd

from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter


def test_canAssertTrue():
    assert True
    
def test_canCreateObject():
    temp = algo_grammar.AddrParser('8 Queensland Ct')
    assert type(temp) is algo_grammar.AddrParser

def test_basicParse():
    temp = algo_grammar.AddrParser('8 Queensland Ct')
    assert temp.get_addrs() == ['8 queensland ct']
    
def test_parens():
    temp = algo_grammar.AddrParser('100 jerusalem ave (hampshire house apts)')
    assert temp.get_addrs() == ['100 jerusalem ave']
    
def test_commaDelimiter():
    temp = algo_grammar.AddrParser('2221, 2223 & 2227 washington st')
    assert temp.get_addrs() == ['2221 washington st', '2223 washington st', '2227 washington st']

def test_andDelimiter():
    temp = algo_grammar.AddrParser('825 and 831 k st')
    assert temp.get_addrs() == ['825 k st', '831 k st']
    
def test_andDelimiter_2():
    temp = algo_grammar.AddrParser('1200 electric avenue and 499 santa clara ave')
    assert temp.get_addrs() == ['1200 electric avenue', '499 santa clara ave']

def test_andDelimiter_3():
    temp = algo_grammar.AddrParser('2810 and 2820 w charleston blvd')
    assert temp.get_addrs() == ['2810 w charleston blvd', '2820 w charleston blvd']
    
def test_andInWord():
    temp = algo_grammar.AddrParser('111 and 223 w anderson ln')
    assert temp.get_addrs() == ['111 w anderson ln', '223 w anderson ln']

def test_andInWord_2():
    temp = algo_grammar.AddrParser('430 buckland hills drive and 110 slater st')
    assert temp.get_addrs() == ['430 buckland hills drive', '110 slater st']

'''    
def test_hwy():
    temp = algo_grammar.AddrParser('3000 hwy 5 and 7090 arbor pkwy')
    assert temp.get_addrs() == ['3000 hwy 5', '7090 arbor pkwy']
'''

def test_semicolonDelimiter():
    temp = algo_grammar.AddrParser('1337 n fiddlesticks place; 2421 cornerstone place')
    assert temp.get_addrs() == ['1337 n fiddlesticks place', '2421 cornerstone place']
    
def test_spaceDelimiter():
    temp = algo_grammar.AddrParser('3860 3880 and 3898 tamiami trl n')
    assert temp.get_addrs() == ['3860 tamiami trl n', '3880 tamiami trl n', '3898 tamiami trl n']


def test_through():
    temp = algo_grammar.AddrParser('1031 through 1043 ster')
    assert temp.get_addrs() == ['1031-1043 ster']
    
def test_blank_address():
    temp = algo_grammar.AddrParser('')
    assert temp.get_flags() == ['Err_00 : No Address Record']

def test_splitter_single_count():
    temp_df = pd.DataFrame(np.array([[0,['1419 sierra creek way']]]), columns = ['TempID','parsed_addr'])
    response = addr_splitter.split_df_addresses(temp_df)
    assert response.shape == (1,3)

def test_splitter_single_addr():
    temp_df = pd.DataFrame(np.array([[0,['1419 sierra creek way']]]), columns = ['TempID','parsed_addr'])
    response = addr_splitter.split_df_addresses(temp_df)
    assert response.iloc[0,2] == '1419 sierra creek way'