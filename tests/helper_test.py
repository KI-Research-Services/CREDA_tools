# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 18:52:51 2020

@author: fisherd
"""

from CREDA_tools import helper
import pytest

def test_init_project_file():
    with pytest.raises(FileNotFoundError):
        helper.CREDA_Project("addresses", "no_good_file.txt")

def test_init_project_type():
    with pytest.raises(ValueError):
        helper.CREDA_Project("addreses", "test_data/san_jose_d1.csv")
        
def test_init_address_missing_column():
    with pytest.raises(KeyError):
        helper.CREDA_Project("addresses", "test_data/bad_file.csv")