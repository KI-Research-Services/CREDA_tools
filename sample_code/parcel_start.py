# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 00:29:44 2020

@author: fisherd
"""

from CREDA_tools import helper

project = helper.CREDA_Project("parcels", "CREDA_tools/test_data/san_jose_shapes.csv")

project.save_all("UBID1.csv")
